from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
from lib.index import hash_file
from lib.anidb.endpoints import AuthRequest, LogoutRequest
from os.path import isfile
from threading import Timer

class Logger(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event)

class NewFileIndexer(FileSystemEventHandler):
    interval = 10
    timer = None
    queue = set()

    """
        This listens on FileCreatedEvent and FileModifiedEvents because when files are moved/copied into
        a directory, the FileCreatedEvent fires immediately, followed by many FileModifiedEvents as the file
        is copied. We want to catch the final event per file, so just listen on everything until things calm down.
    """
    def on_any_event(self, event):
        path = event.src_path

        if isinstance(event, FileCreatedEvent) or isinstance(event, FileModifiedEvent):
            # add the path to the set
            self.queue.add(path)

            # if theres already a timer, cancel it
            if self.timer:
                self.timer.cancel()

            # create and start a new timer to process the queue
            # TODO: this probably isn't efficient considering how many FileModifiedEvents hit
            # maybe record the last event time and let process_queue decide if it should run or start a new timer?
            self.timer = Timer(self.interval, self.process_queue)
            self.timer.start()

    # process the current queue of paths
    def process_queue(self):
        print('processing queue')
        queue = list(self.queue)

        AuthRequest().doRequest()
        while len(queue):
            path = queue.pop()
            if isfile(path):
                print(path)
                hash_file(path)
        LogoutRequest().doRequest()

# test logging observer
def watch_for_all(path):
    logger = Logger()
    observer = Observer()
    observer.schedule(logger, path, recursive=True)
    observer.start()
    import time
    try:
        while True:
            time.sleep(1)
    except Exception as e:
        observer.stop()
    observer.join()

# watch a directory for new files and directories
def watch_for_new(path):
    indexer = NewFileIndexer()
    observer = Observer()
    observer.schedule(indexer, path, recursive=True)
    observer.start()
    print('started observing',path,'for new files')
