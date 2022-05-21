from os import walk, rename, path
from tempfile import TemporaryFile
from sys import argv
from cryptography_engine import Decrypter, TokenError

class FileDecoder:

    def __init__(self, passwd : str = None, salt : bytes = None) -> None:
        self.passwd = passwd or 'default'
        self.salt = salt
        self.file_path = None
        self.new_path = None
        self.tmp = TemporaryFile()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and not str(exc_val).startswith('No File'):
            #print(exc_type, exc_val)
            self.restore_file()
        self.tmp.close()

    def decode_file(self, file_path):
        self.file_path = file_path
        if not path.isfile(file_path):
            raise FileNotFoundError(f'No File {file_path}')
        
        try:
            with open(file_path, 'r+b') as file:
                file_content = file.read()
                self.tmp.write(file_content)
                self.tmp.seek(0)

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
                    self.decode_file(file_path)

        if bad_dir_list:
            raise FileExistsError(*bad_dir_list)

    def restore_file(self):
        with open(self.file_path, 'wb') as file:
            tmp_content = self.tmp.read()
            file.write(tmp_content)

    def __del__(self):
        self.tmp.close()

if __name__ == '__main__':
    # my_decoder = FileDecoder()
    # my_decoder.decode_all(r'.\Nowy_Folder')

    if len(argv) == 2:
        if path.isfile(argv[1]):
            with FileDecoder() as decoder:
                decoder.decode_file(argv[1])
        elif path.isdir(argv[1]):
            with FileDecoder() as decoder:
                decoder.decode_all(argv[1])
        else:
            print('file error')
    else:
        with FileDecoder() as decoder:
            decoder.decode_all(r'.\Nowy_Folder')