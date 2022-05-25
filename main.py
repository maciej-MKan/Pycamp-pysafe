"""Main module of PySafe with argument and configuration logic

    Raises:
        err: acces denied when password is incorect
    """
from getpass import getpass
from os import path
from typing import Sequence, Any
from argparse import Namespace, ArgumentParser, FileType, Action, RawTextHelpFormatter

from file_coder import FileEncoder, FileDecoder, FileOpener, TokenError
from configurator import UserConfig

class GetPassword(Action):
    """Class to handle parser actions with hidden password input."""

    def __call__(self, parser: ArgumentParser, namespace: Namespace, values: str or Sequence[Any] or None, option_string: str or None = ...) -> None:

        values = values or getpass()

        setattr(namespace, self.dest, values)



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
            with FileDecoder(args.password, configuration.salt) as decoder:
                decoder.decode_all(args.decrypt)

        if args.encrypt:
            with FileEncoder(args.password, configuration.salt) as encoder:
                encoder.encode_all(args.encrypt)

        if args.edit:
            with FileOpener(args.password, configuration.salt)as opener:
                opener.execute(*args.edit)

    except (TokenError, FileNotFoundError) as err:
        print(err)
