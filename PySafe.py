#!/usr/bin/env python3.8
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-

"""Main module of PySafe with argument and configuration logic

    usage: PySafe [-h] [-d [option: start / stop]] (-e file | -en [file or dir [file or dir ...]] | -de [file or dir [file or dir ...]]) [Password]

    Raises:
        err: acces denied when password is incorect
    """
from getpass import getpass
from typing import Sequence, Any
from argparse import Namespace, ArgumentParser, Action, RawTextHelpFormatter

from file_coder import FileEncoder, FileDecoder, FileOpener, TokenError
from configurator import UserConfig

class GetPassword(Action):
    """Class to handle parser actions with hidden password input."""

    def __call__(self, parser: ArgumentParser, namespace: Namespace,\
        values: str or Sequence[Any] or None, option_string: str or None = ...) -> None:

        values = values or self.get_password()

        setattr(namespace, self.dest, values)

    def get_password(self):
        passwd = getpass()
        print('*' * len(passwd))
        confirm_passwd = getpass('Confirm password: ')
        if passwd != confirm_passwd:
            print('not match!')
            self.get_password()




if __name__ == '__main__':

    arg_parser = ArgumentParser(
        description="Personal data protector.",
        formatter_class=RawTextHelpFormatter,
        prog='PySafe'
        )
    arg_parser.add_argument(
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
    arg_parser.add_argument(
        '-d',
        '--daemon',
        choices=['start', 'stop'],
        type=str,
        nargs='?',
        metavar='option: start / stop',
        dest="daemon",
        help="""\
            The process of automatically encoding files dumped into a specific folder.
            The option will be available as you ask nicely :)
            \
            """
    )
    option = arg_parser.add_mutually_exclusive_group()
    option.required = True
    option.add_argument(
        '-e',
        '--edit',
        action='extend',
        nargs=1,
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
            Can be a list of files and dirs
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
            Can be a list of files and dirs
            """
    )

    args : Namespace = arg_parser.parse_args()

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
