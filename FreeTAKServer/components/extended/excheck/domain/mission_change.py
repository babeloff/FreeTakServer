from FreeTAKServer.components.core.abstract_component.cot_node import CoTNode
from FreeTAKServer.components.core.abstract_component.cot_property import CoTProperty

class MissionChange(CoTNode):
    def __init__(self, configuration, model, oid=None):
        super().__init__(self.__class__.__name__, configuration, model, oid)

    @CoTProperty
    def contentResource(self):
        data = self.cot_attributes.get("contentResource", None)
        if data is None:
            raise AttributeError("attribute 'contentResource' doesnt exist")
        return data

    @contentResource.setter
    def contentResource(self, contentResource):
        self.cot_attributes["contentResource"] = contentResource

    @CoTProperty
    def creatorUid(self):
        data = self.cot_attributes.get("creatorUid", None)
        if data is None:
            raise AttributeError("attribute 'creatorUid' doesnt exist")
        return data

    @creatorUid.setter
    def creatorUid(self, creatorUid):
        self.cot_attributes["creatorUid"] = creatorUid

    @CoTProperty
    def missionName(self):
        data = self.cot_attributes.get("missionName", None)
        if data is None:
            raise AttributeError("attribute 'missionName' doesnt exist")
        return data

    @missionName.setter
    def missionName(self, missionName):
        self.cot_attributes["missionName"] = missionName

    @CoTProperty
    def timestamp(self):
        data = self.cot_attributes.get("timestamp", None)
        if data is None:
            raise AttributeError("attribute 'timestamp' doesnt exist")
        return data

    @timestamp.setter
    def timestamp(self, timestamp):
        self.cot_attributes["timestamp"] = timestamp

    @CoTProperty
    def type(self):
        data = self.cot_attributes.get("type", None)
        if data is None:
            raise AttributeError("attribute 'type' doesnt exist")
        return data

    @type.setter
    def type(self, type):
        self.cot_attributes["type"] = type
