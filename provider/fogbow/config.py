import json
from constants import FOGBOW_KEY
from constants import RAS_KEY
from constants import AS_KEY
from constants import URL_JSON_KEY

class ConfigHolder():
    def __init__(self, config_path):
        json_data_file = open(config_path,'r+')
        self.data = json.load(json_data_file)
        json_data_file.close()
    
    def get_ras_property(self, _property):
        return self.data[FOGBOW_KEY][RAS_KEY][_property]

    def get_as_property(self, _property):
        return self.data[FOGBOW_KEY][AS_KEY][_property]
    
    def get_endpoint_from_ras(self, endpoint):
        ras = self.data[FOGBOW_KEY][RAS_KEY]
        return ras[endpoint].format(ras[URL_JSON_KEY])

    def get_endpoint_from_as(self, endpoint):
        _as = self.data[FOGBOW_KEY][AS_KEY]
        return _as[endpoint].format(_as[URL_JSON_KEY])
