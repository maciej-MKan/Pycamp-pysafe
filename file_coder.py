from os import rename, path, walk
from time import sleep
from tempfile import TemporaryFile
from cryptography_engine import Encrypter

class FileCoder:
    def __init__(self, passwd : str = None, salt : bytes = None) -> None:
        self.passwd = passwd or 'default'
        self.salt = salt
        self.tmp = TemporaryFile()
        self.file_path = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.restore_file()
        self.tmp.close()

    def encode_file(self, file_path, _retrys = 0):
        self.file_path = file_path

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
                self.encode_file(file_path, _retrys)
            #print(content)
            else:
                with open(new_path, 'rb') as file:
                    file_content = file.read()
                    self.tmp.write(file_content)
                    self.tmp.seek(0)
                    #print(file_content)
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
                    self.encode_file(file_path)

        if bad_dir_list:
            raise FileExistsError(*bad_dir_list)

    def restore_file(self):
        with open(self.file_path, 'wb') as file:
            tmp_content = self.tmp.read()
            file.write(tmp_content)
