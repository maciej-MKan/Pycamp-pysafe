"""here will be the daemon service class
    """

import multiprocessing
from time import sleep
from typing import Callable, Any, Iterable, Mapping

from path_listener import PathListener
from configurator import UserConfig
from file_coder import FileCoder, FileDecoder, TokenError

class PathListenerProcess(multiprocessing.Process):
    def __init__(self):
        super(PathListenerProcess, self).__init__()
        self.passwd = None
        self.mode = None
        self.listener = None
        self.configuration = None
        self.stop = False

    def run(self):
        self._get_config()
        print(self.configuration.pysafe_dir)
        self._start_listener()
        print('daemon started')
        try:
            while not self.stop:
                sleep(5)
                print('daemon loop')
            self.listener = None

        except KeyboardInterrupt:
            pass

    def _get_config(self):
        try:
            self.configuration = UserConfig(self.passwd)
            self.configuration.daemon_mode = self.mode
            self.configuration.read_config()
        except TokenError as err:
            print(err)

    def _start_listener(self):
        self.listener = PathListener(self.created_file_handler, on_modified=print, path=self.configuration.pysafe_dir)
        self.listener.start_listening()

    def created_file_handler(self, event):
        if event.is_directory == False:
            with FileCoder(self.configuration.passwd, self.configuration.salt) as coder:
                coder.execute(event.src_path)

    def __del__(self):
        del self.listener
        print('stop daemon')

if __name__ == '__main__':
    daemon = PathListenerProcess()
    daemon.daemon = True
    daemon.passwd = 'def'
    daemon.mode = 'run'
    daemon.start()
    try:
        while True:
            sleep(10)
            print('main loop')
    except KeyboardInterrupt:
        #daemon.stop = True
        #daemon.join()
        print('bye')
