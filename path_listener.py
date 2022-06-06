import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class EventHandler(FileSystemEventHandler):
    def __init__(self, on_created, on_modified, on_closed) -> None:
        super().__init__()
        self.on_created_foo = on_created or self.no_needed_event
        self.on_modified_foo = on_modified or self.no_needed_event
        self.on_closed_foo = on_closed or self.no_needed_event

    @staticmethod
    def no_needed_event(event):
        pass

    def on_created(self, event):
        super().on_created(event)
        self.on_created_foo(event)

    def on_modified(self, event):
        super().on_modified(event)
        self.on_modified_foo(event)

    def on_closed(self, event):
        super().on_closed(event)
        self.on_closed(event)


class PathListener:
    def __init__(self, on_created = None, on_modified = None, on_closed = None, path = '.') -> None:
        self.path = path
        self.observer = Observer()
        self.event_handler = EventHandler(on_created=on_created, on_modified=on_modified, on_closed=on_closed)


    def start_listening(self):
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
        print('start watching')

    def __del__(self):
        print('stop')
        self.observer.stop()
        self.observer.join()

def test_handler(event):
    print(event.event_type)
    print('dir' if event.is_directory else 'file')
    print(event.src_path)

if __name__ == '__main__':
    my_listener = PathListener(test_handler, path='nowy_folder')
    try:
        my_listener.start_listening()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        del my_listener
