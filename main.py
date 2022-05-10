from time import sleep
from path_listener import PathListener

if __name__ == '__main__':
    my_listener = PathListener(print, path=r'.\Nowy Folder')
    my_listener.start_listening()
    while True:
        sleep(1)
