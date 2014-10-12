from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
from lib.index import hash_file
from lib.anidb.endpoints import AuthRequest, LogoutRequest
from os.path import isfile
from threading import Timer
from time import time
from math import floor

class Logger(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event)

class NewFileIndexer(FileSystemEventHandler):
    interval = 10
    timer = None
    queue = set()
    last_event = 0

    def __init__(self):
        self.update_last_event_time()

    def update_last_event_time(self):
        self.last_event = floor(time())

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
            self.start_timer()

            # update the last event time
            self.update_last_event_time()

    def start_timer(self):
        if not self.timer:
            self.timer = Timer(self.interval, self.process_queue)
            self.timer.start()

    # process the current queue of paths
    def process_queue(self):
        # remove the timer
        self.timer = None

        # check its been long enough sine the last event
        now = floor(time())
        print(now, self.last_event, now - self.last_event, self.interval)
        if now - self.last_event < self.interval:
            # start a new timer if it hasnt
            self.start_timer()
            return

        print('processing queue')
        # get a list from the current queue and clear it
        queue = list(self.queue)
        self.queue.clear()

        # auth with anidb and index all the queued paths
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
