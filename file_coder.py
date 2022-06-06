"""Module with mechanism of file coding"""

import pathlib
from abc import ABC, abstractmethod
from os import rename, path, walk, system
from time import sleep
from tempfile import TemporaryFile
from cryptography_engine import Crypto, TokenError

class Coder(ABC):
    """Coder class template with necessary methods

    attribiuts:
        passwd(str): password of coder
        salt(bytes): salt of coder
    """
    def __init__(self, passwd : str = None, salt : bytes = None) -> None:
        self.passwd = passwd or 'default'
        self.salt = salt
        self.file_path = None
        self.new_path = None
        self.tmp = TemporaryFile()

    @abstractmethod
    def execute(self, file_path : str, _retrys : int):
        """An abstract method that performs an operation on a file

        Args:
            file_path (str): path of executing file
        """

    @staticmethod
    def parse_files(dirs):
        """method looking for files in given paths

        Args:
            dirs (list or tuple): paths or files to search

        Returns:
            tuple, list: files found, paths that are not files
        """
        bad_dir_list = []
        files = []

        for single_dir in dirs:

            if path.isdir(single_dir):
                files_tree = walk(single_dir)
                for files_path in files_tree:
                    for file in files_path[-1]:
                        files.append(f'{files_path[0]}\\{file}')
            elif path.isfile(single_dir):
                files.append(single_dir)

            else:
                bad_dir_list.append(single_dir)
                continue

        return tuple(files), bad_dir_list

    def backup_file(self):
        """creates a backup of the currently processing file"""
        #print('backup ', self.file_path)
        with open(self.file_path, 'rb') as fsrc:
            self.tmp.write(fsrc.read())

    def restore_file(self):
        """restore file from backup"""
        with open(self.file_path, 'wb') as fdst:
            fdst.write(self.tmp.read())

    @staticmethod
    def file_filter(paths: tuple, patterns : tuple = ('*',), patterns_wo : tuple = ('!*',)):
        """file filter in terms of extension

        Args:
            paths (tuple): tuple of files
            patterns (tuple, optional): Pattern dla porządanych rozszerzeń. Np '.txt','.bmp',..\
                Defaults to ('*',) for all files.
            patterns_wo (tuple, optional): Pattern for unwanted files. E.g. '.txt', '. Bmp',..\
                Defaults to ('!*',) for any files.
        """

        return(tuple(file_path for file_path in paths\
            for pattern in patterns if pathlib.Path(file_path).match(pattern)\
                and all(not pathlib.Path(file_path).match(wo) for wo in patterns_wo)))

    def __enter__(self):
        """enter method for use as context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit method for use as context manager.
        If an error occurs while using the manager, restore the file from the backup.
        Otherwise, it removes it.
        """
        if exc_type and not str(exc_val).startswith('No File'):
            #print(exc_type, exc_val)
            self.restore_file()
        self.tmp.close()

    def __del__(self):
        """method performed during class termination
        removes the tmp file"""
        self.tmp.close()
        #print('tmp closeds')

class FileEncoder(Coder):
    """File encoder class
    """

    def execute(self, file_path : str, _retrys : int = 60):
        """Main method of file encoder

        Args:
            file_path (str): path to file for encoding
            _retrys (int, optional): Number of retries when the file was not accessed.\
                Defaults to 60.

        Raises:
            TimeoutError: Exception when the file cannot be accessed
        """
        self.file_path = file_path

        self.backup_file()

        if _retrys > 0:
            extension = pathlib.Path(file_path).suffix
            new_path = self._generate_file_name(file_path)
            pre_content = f'{extension}<>'.encode('utf-8')
            #print(new_path)
            try:
                rename(file_path, new_path)
            except PermissionError as err:
                print(err)
                sleep(1)
                self.execute(file_path, _retrys = _retrys - 1)
            #print(content)
            else:
                with open(new_path, 'rb') as file:
                    file_content = file.read()
                with open(new_path, 'wb') as file:
                    content = Crypto(self.passwd, self.salt).encrypt(pre_content + file_content)
                    #print(content)
                    file.write(content)
        else:
            raise TimeoutError('no access to file')

    def _generate_file_name(self, cur_path : str, count : int = 0):
        """internal method generating a new extension for the encoded file

        Args:
            cur_path (str): original file path
            count (int, optional): Own paranet. It should not be overwritten

        Returns:
            str: file path with new extension
        """
        suffix = '.pys' + f'({count})' if count else '.pys'
        new_path = pathlib.Path(cur_path).with_suffix(suffix)
        if path.isfile(new_path):
            new_path = self._generate_file_name(cur_path, count=count+1)
        return new_path

    def encode_all(self, dirs: tuple):
        """A method to process a tuple containing the paths of the files and folders to be encoded

        Args:
            dirs (tuple): tuple with paths

        Raises:
            FileExistsError: list of wrong paths
        """

        files, bad_dir_list = self.parse_files(dirs)

        for file_path in self.file_filter(files, patterns_wo=('*.pys', '*.pys(*)')):
            self.execute(file_path)

        if bad_dir_list:
            raise FileExistsError(*bad_dir_list)

    def __del__(self):
        super().__del__()

class FileDecoder(Coder):
    """Files decorer class
    """

    def execute(self, file_path: str, _retrys : int = 0):
        """Main method of file decoder

        Args:
            file_path (str): path to file for decoding
            _retrys (int, optional): Number of retries when the file was not accessed.

        Raises:
            FileNotFoundError: exception when an invalid file is given
            errtoken: exception when incorrect access data was provided
        """
        self.file_path = file_path

        if not path.isfile(file_path):
            raise FileNotFoundError(f'No File {file_path}')

        try:
            with open(file_path, 'r+b') as file:
                file_content = file.read()
                self.backup_file()

                decrypted_content = Crypto(self.passwd, self.salt).decrypt(file_content)

                file_extension, *content = decrypted_content.split(b'<>')
        except TokenError as errtoken:
            if _retrys > 0:
                _retrys -= 1
                self.execute(self.file_path, _retrys)
            else:
                raise errtoken

        else:

            with open(file_path, 'w+b') as file:
                file.write(b'<>'.join(content))

            new_path = pathlib.Path(file_path).with_suffix(file_extension.decode('utf-8'))
            try:
                rename(file_path, new_path)
                self.new_path = new_path
            except PermissionError as err:
                print(err)


    def decode_all(self, dirs):
        """A method to process a tuple containing the paths of the files and folders to be decoded

        Args:
            dirs (tuple): tuple with paths

        Raises:
            FileExistsError: list of wrong paths
        """
        files, bad_dir_list = self.parse_files(dirs)

        for file_path in self.file_filter(files, patterns=('*.pys', '*.pys(*)')):
            self.execute(file_path)

        if bad_dir_list:
            raise FileExistsError(*bad_dir_list)

    def __del__(self):
        super().__del__()

class FileOpener(Coder):
    """Encrypted file editing class"""

    def execute(self, *file_path : str):
        """main method to procesing file"""
        file_path = ' '.join(file_path)
        if path.isfile(file_path):
            self.file_path = file_path

            self.backup_file()

            self._decode_file()
            self._run_file_editor()
            self._encode_file()
        else:
            if not file_path.endswith('.pys'):
                self.execute(file_path + '.pys')
            else:
                raise FileNotFoundError(f'No File {file_path}')

    def _decode_file(self):
        """internal method to decrypt file"""
        with FileDecoder(self.passwd, self.salt) as decoder:
            decoder.execute(self.file_path)
            self.new_path = decoder.new_path

    def _run_file_editor(self):
        """internal method to run decrypted file in default sys editor"""
        if self.new_path:
            system(f'"{self.new_path}"')

    def _encode_file(self):
        """internal method to encrypt file back"""
        with FileEncoder(self.passwd, self.salt) as coder:
            coder.execute(self.new_path, 5)
