from os import rename
from time import sleep
from path_listener import PathListener
from file_coder import FileCoder


def created_file_handler(event):
    if event.is_directory == False:
        with FileCoder() as coder:
            coder.encode_file(event.src_path)

if __name__ == '__main__':
    my_listener = PathListener(created_file_handler, path=r'.\Nowy_Folder')
    try:
        my_listener.start_listening()
        while True:
            sleep(1)
    except KeyboardInterrupt:
        del my_listener
