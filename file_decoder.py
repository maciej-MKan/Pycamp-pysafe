from os import walk, rename, path

class FileDecoder:

    def __init__(self, passwd = None) -> None:
        self.passwd = passwd or 'default'

    def decode_file(self, file_path):
        if not path.isfile(file_path):
            raise FileNotFoundError
        
        with open(file_path, 'rb') as file:
            file_content = file.read()
            file_extension, passwd, content = file_content.split(b'<>')

        with open(file_path, 'wb') as file:
            file.write(content)

        new_path, _ = path.splitext(file_path)
        new_path += file_extension.decode('utf-8')
        try:
            rename(file_path, new_path)
        except PermissionError as err:
            print(err)

    def decode_all(self, dir):
        if not path.isdir(dir):
            raise FileNotFoundError
        
        files_tree = walk(dir)
        files = []
        for files_path in files_tree:
            for file in files_path[-1]:
             files.append(f'{files_path[0]}\\{file}')

        for file_path in files:
            _, file_extension = path.splitext(file_path)
            if file_extension.startswith('.pys'):
                self.decode_file(file_path)

if __name__ == '__main__':
    my_decoder = FileDecoder()
    my_decoder.decode_all(r'.\Nowy_Folder')