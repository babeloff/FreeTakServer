#######################################################
# 
# ReceiveConnections.py
# Python implementation of the Class ReceiveConnections
# Generated by Enterprise Architect
# Created on:      19-May-2020 6:21:05 PM
# Original author: Natha Paquette
# 
#######################################################
import asyncio
import socket
import logging
import logging.handlers
import re
from lxml import etree
import ssl
import time
import os
from typing import Union

from FreeTAKServer.controllers.configuration.ClientReceptionLoggingConstants import ClientReceptionLoggingConstants
from FreeTAKServer.controllers.configuration.LoggingConstants import LoggingConstants
from FreeTAKServer.model.RawConnectionInformation import RawConnectionInformation as sat
from FreeTAKServer.controllers.CreateLoggerController import CreateLoggerController
from FreeTAKServer.controllers.configuration.ReceiveConnectionsConstants import ReceiveConnectionsConstants
from FreeTAKServer.controllers.connection.SSLSocketController import SSLSocketController

loggingConstants = LoggingConstants(log_name="FTS_ReceiveConnections")
logger = CreateLoggerController("FTS_ReceiveConnections", logging_constants=loggingConstants).getLogger()

loggingConstants = ClientReceptionLoggingConstants()

TEST_SUCCESS = "success"
END_OF_MESSAGE = b"</event>"

# TODO: move health check values to constants and create controller for HealthCheck data

class ReceiveConnections:
    connections_received = 0

    def receive_connection_data(self, client) -> Union[etree.Element, str]:
        """this method is responsible for receiving connection data from the client

        Args:
            client (socket.socket): _description_

        Raises:
            Exception: if data returned by client is empty

        Returns:
            Union[etree.Element, str]: in case of real connection an etree Element should be returned containing client connection data
                                        in case of test connection TEST_SUCCESS const should be returned
        """        
        client.settimeout(int(ReceiveConnectionsConstants().RECEIVECONNECTIONDATATIMEOUT))
        part = client.recv(1)
        if part == b"": raise Exception('empty data')
        client.settimeout(10)
        client.setblocking(True)
        xmlstring = self.recv_until(client, b"</event>").decode()
        if part.decode()+xmlstring == ReceiveConnectionsConstants().TESTDATA: return TEST_SUCCESS
        client.setblocking(True)
        client.settimeout(int(ReceiveConnectionsConstants().RECEIVECONNECTIONDATATIMEOUT))
        xmlstring = "<multiEvent>" + part.decode() + xmlstring + "</multiEvent>"  # convert to xmlstring wrapped by multiEvent tags
        xmlstring = re.sub(r'(?s)\<\?xml(.*)\?\>', '',
                           xmlstring)  # replace xml definition tag with empty string as it breaks serilization
        events = etree.fromstring(xmlstring)
        return events

    def listen(self, sock, sslstatus=False):
        # logger = CreateLoggerController("ReceiveConnections").getLogger()
        # listen for client connections
        sock.listen(ReceiveConnectionsConstants().LISTEN_COUNT)
        try:
            # establish the socket variables
            if sslstatus == True:
                socket.setdefaulttimeout(ReceiveConnectionsConstants().SSL_SOCK_TIMEOUT)
                sock.settimeout(ReceiveConnectionsConstants().SSL_SOCK_TIMEOUT)
            # logger.debug('receive connection started')
            try:
                client, address = sock.accept()
                if sslstatus == True:
                    client = asyncio.run(asyncio.wait_for(SSLSocketController().wrap_client_socket(client), timeout=ReceiveConnectionsConstants().WRAP_SSL_TIMEOUT))
            except ssl.SSLError as e:
                print(e)
                client.close()
                logger.warning('ssl error thrown in connection attempt ' + str(e))
                return -1

            except asyncio.TimeoutError as e:
                client.close()
                logger.warning('timeout error thrown in connection attempt '+str(e))
                return -1

            if sslstatus == True:
                logger.info('client connected over ssl ' + str(address) + ' ' + str(time.time()))
            # wait to receive client
            try:
                events = self.receive_connection_data(client=client)
            except Exception as e:
                try:
                    events = self.receive_connection_data(client=client)
                except Exception as e:
                    client.close()
                    logger.warning("receiving connection data from client failed with exception "+str(e))
                    return -1
            # TODO: move out to separate function
            if events == TEST_SUCCESS:
                client.send(b'success')
            client.settimeout(0) # set the socket to non blocking
            logger.info(loggingConstants.RECEIVECONNECTIONSLISTENINFO)
            # establish the socket array containing important information about the client
            raw_connection_information = self.instantiate_client_object(address, client, events)
            logger.info("client accepted")
            try:
                if socket is not None and raw_connection_information.xmlString != b'':
                    return raw_connection_information
                else:
                    logger.warning("final socket entry is invalid")
                    client.close()
                    return -1
            except Exception as e:
                client.close()
                logger.warning('exception in returning data ' + str(e))
                return -1

        except Exception as e:
            logger.warning(loggingConstants.RECEIVECONNECTIONSLISTENERROR)
            try:
                client.close()
            except Exception as e:
                pass
            finally:
                return -1

    def instantiate_client_object(self, address, client, events):
        raw_connection_information = sat()
        raw_connection_information.ip = address[0]
        raw_connection_information.socket = client
        raw_connection_information.xmlString = etree.tostring(events.findall('event')[0]).decode('utf-8')
        return raw_connection_information

    def recv_until(self, client, delimiter) -> bytes:
        """receive data until a delimiter has been reached

        Args:
            client (socket.socket): client socket
            delimiter (bytes): bytestring representing the delimiter

        Returns:
            Union[None, bytes]: None if no data was received otherwise send received data
        """        
        message = b""
        start_receive_time = time.time()
        client.settimeout(4)
        while delimiter not in message and time.time() - start_receive_time <= ReceiveConnectionsConstants().RECEIVECONNECTIONDATATIMEOUT:
            try:
                message = message + client.recv(ReceiveConnectionsConstants().CONNECTION_DATA_BUFFER)
            except:
                return message
        return message
