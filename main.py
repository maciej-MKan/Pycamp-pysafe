import argparse
from os import path
from configparser import ConfigParser
from time import sleep
from path_listener import PathListener
from file_coder import FileCoder
from file_decoder import FileDecoder

def created_file_handler(event):
    if event.is_directory == False:
        with FileCoder(configuration.passwd, configuration.salt) as coder:
            coder.encode_file(event.src_path)

class UserConfig:

    def __init__(self, password) -> None:
        self.passwd = password
        self.config = ConfigParser()
        self.config_file = 'config'
        self.pysafe_dir = None
        self.salt = None

    def check_config(self):
        try:
            self._decode_config()
        except FileNotFoundError:
            self.create_config()
            sleep(1)
        finally:
            self._encode_config()

    def create_config(self):
        self.config['GENERAL'] = {}
        self.config['GENERAL']['pysafe_folder'] = input('Enter path to PySafe folder : ')
        self.config['GENERAL']['salt'] = 'ecie_pecie'
        with open(f'{self.config_file}.pysc', 'w') as configfile:
            self.config.write(configfile)
        self.config.clear()

    def read_config(self):
        self._decode_config()
        self.config.read(f'{self.config_file}.pysc')
        self.pysafe_dir = self.config['GENERAL']['pysafe_folder']
        self.salt = self.config['GENERAL']['salt'].encode('utf-8')
        self._encode_config()

    def _encode_config(self):
        with FileCoder(self.passwd) as config_coder:
            config_coder.encode_file(f'{self.config_file}.pysc')

    def _decode_config(self):
        with FileDecoder(self.passwd) as config_decoder:
            config_decoder.decode_file(f'{self.config_file}.pys')

if __name__ == '__main__':

    configuration = UserConfig('default')
    configuration.check_config()
    configuration.read_config()
    print(configuration.pysafe_dir)
    print(configuration.salt)

    my_listener = PathListener(created_file_handler,on_modified=print, path=configuration.pysafe_dir)
    try:
        my_listener.start_listening()
        while True:
            sleep(1)
    except KeyboardInterrupt:
        del my_listener