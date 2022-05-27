import pathlib
from os import rename, path, walk, system
from time import sleep
from tempfile import TemporaryFile
from cryptography_engine import Encrypter, Decrypter, TokenError
from abc import ABC, abstractmethod

class Coder(ABC):
    def __init__(self, passwd : str = None, salt : bytes = None) -> None:
        self.passwd = passwd or 'default'
        self.salt = salt
        self.file_path = None
        self.new_path = None
        self.tmp = TemporaryFile(delete=True)

    @abstractmethod
    def execute(self, file_path):
        pass

    def backup_file(self):
        #print('backup ', self.file_path)
        with open(self.file_path, 'rb') as fsrc:
            self.tmp.write(fsrc.read())

    def restore_file(self):
        with open(self.file_path, 'wb') as fdst:
            fdst.write(self.tmp.read())

    def file_filter(paths: tuple, patterns : tuple = ('*',), patterns_wo : tuple = ('!*',)):

        return(tuple(file_path for file_path in paths\
            for pattern in patterns\
            if pathlib.Path(file_path).match(pattern)\
                and all(not pathlib.Path(file_path).match(wo) for wo in patterns_wo)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and not str(exc_val).startswith('No File'):
            #print(exc_type, exc_val)
            self.restore_file()
        self.tmp.close()

    def __del__(self):
        self.tmp.close()
        #print('tmp closeds')

class FileEncoder(Coder):

    def execute(self, file_path, _retrys = 0):
        self.file_path = file_path

        self.backup_file()

        if _retrys < 60:
            _ , extension = path.splitext(file_path)
            new_path = self._generate_file_name(file_path)
            pre_content = f'{extension}<>'.encode('utf-8')
            #print(new_path)
            try:
                rename(file_path, new_path)
            except PermissionError as err:
                print(err)
                sleep(1)
                _retrys += 1
                self.execute(file_path, _retrys)
            #print(content)
            else:
                with open(new_path, 'rb') as file:
                    file_content = file.read()
                with open(new_path, 'wb') as file:
                    content = Encrypter(self.passwd, self.salt).encrypt(pre_content + file_content)
                    #print(content)
                    file.write(content)
        else:
            raise TimeoutError('no access to file')

    def _generate_file_name(self, cur_path : str, count : int = 0):
        new_path = cur_path.split('.')
        new_path[-1] = 'pys' + f'({count})' if count else 'pys'
        new_path = '.'.join(new_path)
        if path.isfile(new_path):
            new_path = self._generate_file_name(new_path, count=count+1)
        return new_path

    def encode_all(self, dirs):
        bad_dir_list = []

        for dir in dirs:
            files = None
            if path.isdir(dir):
                files_tree = walk(dir)
                files = []
                for files_path in files_tree:
                    for file in files_path[-1]:
                        files.append(f'{files_path[0]}\\{file}')
            elif path.isfile(dir):
                files = (dir,)

            else:
                bad_dir_list.append(dir)
                continue

            for file_path in files:
                _, file_extension = path.splitext(file_path)
                if not file_extension.startswith('.pys'):
                    self.execute(file_path)

        if bad_dir_list:
            raise FileExistsError(*bad_dir_list)

    def __del__(self):
        super().__del__()

class FileDecoder(Coder):

    def execute(self, file_path):
        self.file_path = file_path

        if not path.isfile(file_path):
            raise FileNotFoundError(f'No File {file_path}')

        try:
            with open(file_path, 'r+b') as file:
                file_content = file.read()
                self.backup_file()

                decrypted_content = Decrypter(self.passwd, self.salt).decrypt(file_content)

                file_extension, *content = decrypted_content.split(b'<>')
        except TokenError as errtoken:
            raise errtoken

        else:

            with open(file_path, 'w+b') as file:
                file.write(b'<>'.join(content))

            new_path, _ = path.splitext(file_path)
            new_path += file_extension.decode('utf-8')
            try:
                rename(file_path, new_path)
                self.new_path = new_path
            except PermissionError as err:
                print(err)


    def decode_all(self, dirs):
        bad_dir_list = []

        for dir in dirs:
            files = None
            if path.isdir(dir):
                files_tree = walk(dir)
                files = []
                for files_path in files_tree:
                    for file in files_path[-1]:
                        files.append(f'{files_path[0]}\\{file}')
            elif path.isfile(dir):
                files = (dir,)

            else:
                bad_dir_list.append(dir)
                continue

            for file_path in files:
                _, file_extension = path.splitext(file_path)
                if file_extension.startswith('.pys'):
                    self.execute(file_path)

        if bad_dir_list:
            raise FileExistsError(*bad_dir_list)

    def __del__(self):
        super().__del__()

class FileOpener(Coder):
    """Encrypted file editing class"""

    def execute(self, file_path : str):
        """main method to procesing file"""
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
        """innet method to decrypt file"""
        with FileDecoder(self.passwd, self.salt) as decoder:
            decoder.execute(self.file_path)
            self.new_path = decoder.new_path

    def _run_file_editor(self):
        """inner method to run decrypted file in default sys editor"""
        if self.new_path:
            system(f'"{self.new_path}"')

    def _encode_file(self):
        """inner method to encrypt file back"""
        with FileEncoder(self.passwd, self.salt) as coder:
            coder.execute(self.new_path, 5)