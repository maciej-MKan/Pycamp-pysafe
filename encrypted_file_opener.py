"""Encrypted file editing module"""

from os import system, path
from sys import argv
from file_decoder import FileDecoder
from file_coder import FileCoder

class FileOpener:
    """Encrypted file editing class"""

    def __init__(self, file_path, password : str, salt : bytes = None) -> None:
        self.passwd = password
        self.file_path = file_path
        self.salt = salt
        self.decrypted_file_path = None

    def execute(self):
        """main method to procesing file"""
        self._decode_file()
        self._run_file_editor()
        self._encode_file()

    def _decode_file(self):
        """innet method to decrypt file"""
        with FileDecoder(self.passwd, self.salt) as decoder:
            decoder.decode_file(self.file_path)
            self.decrypted_file_path = decoder.new_path

    def _run_file_editor(self):
        """inner method to run decrypted file in default sys editor"""
        if self.decrypted_file_path:
            system(self.decrypted_file_path)

    def _encode_file(self):
        """inner method to encrypt file back"""
        with FileCoder(self.passwd, self.salt) as coder:
            coder.encode_file(self.decrypted_file_path, 5)

if __name__ == '__main__':
    if len(argv) == 2 and path.isfile(argv[1]):
        opener = FileOpener('default', argv[1])
        opener.execute()
