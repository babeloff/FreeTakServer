from lxml import etree
from digitalpy.core.impl.default_factory import DefaultFactory
from digitalpy.config.impl.inifile_configuration import InifileConfiguration
from digitalpy.core.object_factory import ObjectFactory
from unittest.mock import MagicMock
from FreeTAKServer.components.extended.emergency.configuration.emergency_constants import (
    TYPE_MAPPINGS,
)
from FreeTAKServer.components.extended.emergency.emergency_facade import Emergency
from FreeTAKServer.components.core.type.type_facade import Type
from FreeTAKServer.components.core.domain.domain_facade import Domain
from FreeTAKServer.controllers.XMLCoTController import XMLCoTController
from FreeTAKServer.controllers.services.FTS import FTS
from FreeTAKServer.model.ServiceObjects.FTS import FTS as FTSModelVariables
from FreeTAKServer.components.core.xml_serializer.xml_serializer_facade import (
    XMLSerializer,
)
from FreeTAKServer.controllers.services.internal_telemetry_service import TelemetryService
import pytest
import multiprocessing

from tests.test_components.test_utils import execute_action, execute_async_action


def setup_module(module):

    FTS().start_routing_proxy_service(FTSServiceStartupConfigObject=FTSModelVariables())
    multiprocessing.Process(target=TelemetryService().main).start()
    config = InifileConfiguration("")
    config.add_configuration(
        r"C:\Users\natha\PycharmProjects\FreeTakServer\FreeTAKServer\configuration\routing\action_mapping.ini"
    )


def test_domain_health():
    test_data = '<event version="2.0" uid="S-1-5-21-2720623347-3037847324-4167270909-1002-9-1-1" type="b-a-o-tbl" time="2022-08-13T01:30:40.83Z" start="2022-08-13T01:30:40.83Z" stale="2022-08-13T01:40:40.83Z" how="h-e"><point lat="27.0196007365431" lon="-41.1839609383656" hae="9999999" ce="9999999" le="9999999" /><detail><link type="a-f-G-U-C-I" uid="S-1-5-21-2720623347-3037847324-4167270909-1002" relation="p-p" /><contact callsign="DATA-Alert" /><emergency type="Alert">DATA</emergency></detail></event>'
    mock_message = MagicMock()
    mock_message.xmlString = test_data
    mock_message.clientInformation = "test"

    health_check_output = execute_action("HealthCheck", {})

    assert health_check_output["health"] == True


def test_domain_metrics():
    execute_async_action("TestMetrics", {})

    get_metrics_output = execute_async_action("GetMetrics", {})
    assert "metrics" in get_metrics_output


def test_domain_telemetry():
    execute_async_action("TestTracing", {})
    get_telemetry_output = execute_async_action("GetTraces", {})
    assert "traces" in get_telemetry_output


if __name__ == "__main__":
    if True:
        args_str = r"-v tests\test_components\test_core_components\test_domain.py::test_domain_telemetry"
        args = args_str.split(" ")
        retcode = pytest.main(args)
