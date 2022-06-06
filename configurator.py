"""Module supported user configuration"""

from configparser import ConfigParser
from file_coder import FileEncoder, FileDecoder, TokenError

class UserConfig:
    """Class to handle the configparser"""

    def __init__(self, password) -> None:
        self.passwd : str = password
        self.config = ConfigParser()
        self.config_file = 'config' # file name w/o extension
        self.pysafe_dir = None
        self.salt : bytes = None
        self.daemon_mode = None

    def create_config(self):
        """creating new config file method"""

        self.config['GENERAL'] = {}
        if self.daemon_mode:
            self.config['GENERAL']['pysafe_folder'] = input('Enter path to PySafe folder : ')
        self.config['GENERAL']['salt'] = 'ecie_pecie'
        with open(f'{self.config_file}.pysc', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        self.config.clear()
        self._encode_config()

    def read_config(self):
        """Method to read configuration from file

        Raises:
            err: access denied when password is wrong
        """
        try:
            self._decode_config()
            self.config.read(f'{self.config_file}.pysc')
            if self.daemon_mode:
                try:
                    self.pysafe_dir = self.config['GENERAL']['pysafe_folder']
                except KeyError:
                    self.create_config()
            self.salt = self.config['GENERAL']['salt'].encode('utf-8')
        except FileNotFoundError:
            self.create_config()
        except TokenError as err:
            raise err
        else:
            self._encode_config()

    def _encode_config(self):
        """Inner method to encrypt configuration file"""
        with FileEncoder(self.passwd) as config_coder:
            config_coder.execute(f'{self.config_file}.pysc')

    def _decode_config(self):
        """Inner method to decrypt configuration file"""

        with FileDecoder(self.passwd) as config_decoder:
            config_decoder.execute(f'{self.config_file}.pys')
