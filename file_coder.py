from os import rename, path

class FileCoder:
    def __init__(self, passwd = None) -> None:
        self.passwd = passwd or 'default'

    def encode_file(self, file_path):
        new_path = self._generate_file_name(file_path)
        try:
            rename(file_path, new_path)
        except PermissionError as err:
            print(err)
    
    def _generate_file_name(self, cur_path : str, count : int = 0):
        new_path = cur_path.split('.')
        new_path[-1] = 'pys' + f'({count})' if count else 'pys'
        new_path = '.'.join(new_path)
        if path.isfile(new_path):
            new_path = self._generate_file_name(new_path, count=count+1)
        return new_path

    def encode_content_file(self, content):
        added_content = f'header {self.passwd}'
        new_content = added_content + '\n' + content

        return new_content
