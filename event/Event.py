__author__ = 'Dario'

import threading

class Event:
    def __init__(self, func=None):
        self.handlers = set()
        if func:
            self.handle(func)

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

    def fire_threaded(self, *args, **kwargs):
        for handler in self.handlers:
            thread = threading.Thread(target=handler, args = args, kwargs = kwargs)
            thread.start()

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire_threaded
    __len__  = getHandlerCount