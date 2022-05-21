"""Main module of PySafe with argument and configuration logic

    Raises:
        err: acces denied when password is incorect
    """
from getpass import getpass
from os import path
from configparser import ConfigParser
from typing import Sequence, Any
from argparse import Namespace, ArgumentParser, FileType, Action, RawTextHelpFormatter

from file_coder import FileCoder
from file_decoder import FileDecoder, TokenError
from encrypted_file_opener import FileOpener

class GetPassword(Action):
    """Class to handle parser actions with hidden password input."""

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: str or Sequence[Any] or None, option_string: str or None = ...) -> None:

        values = values or getpass()

        setattr(namespace, self.dest, values)

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
        with open(f'{self.config_file}.pysc', 'w') as configfile:
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
        with FileCoder(self.passwd) as config_coder:
            config_coder.encode_file(f'{self.config_file}.pysc')

    def _decode_config(self):
        """Inner method to decrypt configuration file"""

        with FileDecoder(self.passwd) as config_decoder:
            config_decoder.decode_file(f'{self.config_file}.pys')

if __name__ == '__main__':

    parser = ArgumentParser(
        description="Personal data protector.",
        formatter_class=RawTextHelpFormatter,
        prog='PySafe'
        )
    parser.add_argument(
        'password',
        type=str,
        metavar='Password',
        nargs='?',
        default=None,
        action=GetPassword,
        help="""\
            Your Pysafe password.
            Recommended not entered on the command line.
            Leave blank, and then the program will ask you about it in safe mode.\
            """
        )
    parser.add_argument(
        '-d',
        '--daemon',
        choices=['start', 'stop'],
        type=str,
        nargs='?',
        metavar='option: start / stop',
        dest="daemon",
        help="""\
            To Do help
            """
    )
    option = parser.add_mutually_exclusive_group()
    option.required = True
    option.add_argument(
        '-e',
        '--edit',
        action='extend',
        nargs='+',
        metavar='file',
        type=str,
        dest='edit',
        help="""\
            Encrypted file to edit
            """
    )
    option.add_argument(
        '-en',
        '--encrypt',
        action='extend',
        nargs='*',
        metavar='file or dir',
        type=str,
        dest='encrypt',
        help="""\
            File or directory to encrypt
            """
    )
    option.add_argument(
        '-de',
        '--decrypt',
        action='extend',
        nargs='*',
        metavar='file or dir',
        type=str,
        dest='decrypt',
        help="""\
            File or directory to decrypt
            """
    )

    args : Namespace = parser.parse_args()

    configuration = UserConfig(args.password)
    configuration.daemon_mode = args.daemon

    try:
        configuration.read_config()

        if args.decrypt:
            FileDecoder(args.password, configuration.salt).decode_all(args.decrypt)

        if args.encrypt:
            FileCoder(args.password, configuration.salt).encode_all(args.encrypt)

        if args.edit:
            FileOpener(*args.edit, args.password, configuration.salt).execute()

    except TokenError as err:
        print(err)
