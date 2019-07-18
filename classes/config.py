import json

class Config:
    """ This class is used for manage the config file """

    def __init__(self, filepath: str):
        """
        Constructor method. It saves into an attribute the config file path.

        :param filepath: Config file path
        """

        self.filepath = filepath

    def _write_json(self, data: dict):
        """
        This private function is used for writing settings into the config file.

        :param data: config dictionary to write to the config.json file.
        """

        with open(self.filepath, 'w+') as outfile:
            json.dump(data, outfile)
    
    def _read_json(self) -> dict:
        """
        This private function is used for reading all the settings stored in the config file.

        :return: Dictionary built as "setting_name: setting_value" using the config.json file.
        """

        with open(self.filepath) as json_file:
            return json.load(json_file)

    def create_default_file(self):
        """
        This function is used for generating a default config file.
        """
        # TODO: Finish

        default_config = {
            "automaticName": True,
            "saveFolder": "download",
            "overwriteCheck": True,
            "token": "INSERT YOUR TOKEN HERE"
        }

        self._write_json(default_config)

    def check_config_file(self):
        """
        Checks the conformity of the config file. If detects that the config
        file is malformed or damaged (ex. non accessible, ...) this function
        will generate a new one using the 'create_default_file' function.
        """
        # TODO: Finish

        data = self._read_json()
        print("Check if there are all the required settings")

    def get_settings(self):
        """
        Returns all the settings saved in the config file.
        """

        return self._read_json()
