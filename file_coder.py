from os import rename, path
from time import sleep
from tempfile import TemporaryFile
from cryptography_engine import Encrypter

class FileCoder:
    def __init__(self, passwd = None) -> None:
        self.passwd = passwd or 'default'
        self.tmp = TemporaryFile()
        self.file_path = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.restore_file()
        self.tmp.close()

    def encode_file(self, file_path, retrys = 0):
        self.file_path = file_path

        if retrys < 60:
            _ , extension = path.splitext(file_path)
            new_path = self._generate_file_name(file_path)
            pre_content = f'{extension}<>'.encode('utf-8')
            #print(new_path)
            try:
                rename(file_path, new_path)
            except PermissionError as err:
                print(err)
                sleep(1)
                retrys += 1
                self.encode_file(file_path, retrys)
            #print(content)
            else:
                with open(new_path, 'rb') as file:
                    file_content = file.read()
                    self.tmp.write(file_content)
                    self.tmp.seek(0)
                    #print(file_content)
                with open(new_path, 'wb') as file:
                    content = self.encrypt_file_content(pre_content + file_content)
                    #print(content)
                    file.write(content)
        else:
            raise TimeoutError('no access to file')
    
    def _generate_file_name(self, cur_path : str, count : int = 0):
        new_path = cur_path.split('.')
        if count:
            new_path[-2] += f'({count})'
        new_path[-1] = 'pys'
        new_path = '.'.join(new_path)
        if path.isfile(new_path):
            new_path = self._generate_file_name(new_path, count=count+1)
        return new_path

    def encrypt_file_content(self, content : bytes):
        return Encrypter(self.passwd).encrypt(content)

    def restore_file(self):
        with open(self.file_path, 'wb') as file:
            tmp_content = self.tmp.read()
            file.write(tmp_content)
