import json

'''
This class is used for manage the config file
'''
class Config:

    '''
        Constructor method. It saves into an attribute the config file path.
    '''
    def __init__(self, filepath: str):
        self.filepath = filepath

    '''
        This private function is used for writing settings into the config
        file.
    '''
    def _write_json(self, data: dict):
        with open(self.filepath, 'w+') as outfile:  
            json.dump(data, outfile)
    
    '''
        This private function is used for reading all the settings stored in
        the config file.
    '''
    def _read_json(self) -> dict:
        with open(self.filepath) as json_file:  
            return json.load(json_file)

    '''
        This function is used for generating a default config file.
    '''
    def create_default_file():
        default_config = {
            "automaticName": True,
            "saveFolder": "download",
            "overwriteCheck": True,
            "token": "INSERT YOUR TOKEN HERE"
        }

        self._write_json(default_config)

    '''
        Checks the conformity of the config file. If detects that the config
        file is malformed or damaged (ex. non accessible, ...) this function
        will generate a new one using the 'create_default_file' function.
    '''
    def check_config_file(self):
        data = self._read_json()
        print("Check if there are all the required settings")

    '''
        Returns all the settings saved in the config file.
    '''
    def get_settings(self):
        return self._read_json()