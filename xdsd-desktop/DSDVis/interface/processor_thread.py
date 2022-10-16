import ctypes
import inspect
import threading
import time

from PyQt5.QtCore import pyqtSignal, QThread

from DSDPy.src.util.cexception import StopThreadError
from DSDPy.src.basics import graph_processor as gp


class PProcessorThread(QThread):
    my_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(QThread, self).__init__()
        self.stopped = False

    def run(self):
        self.my_signal.emit()
        pass


class ProcessorThread(threading.Thread):
    '''A thread class that supports raising exception in the thread from
       another thread.
       https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread
    '''

    def __init__(self, event, threshold, *args, **kwargs):
        super(ProcessorThread, self).__init__(*args, **kwargs)
        self.pp = PProcessorThread()
        self.event = event
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()
        self.threshold = threshold
        self.stopped = False
        self.lock = threading.Lock()

    def run(self):
        try:
            i = 0
            while not self._args[6][self._args[5]] and i < self.threshold:
                if self.stopped:
                    return
                self.__flag.wait()
                self._args = gp.one_iteration(*self._args)
                print(time.time())
                i += 1
                # time.sleep(1)
                if self.lock.locked():
                    self.lock.release()
            self.event.set()
            self.pp.start()
            print("graph processor finished.")
        except StopThreadError:
            print("Stopped!")

    def pause(self):
        print("is paused")
        self.__flag.clear()

    def resume(self):
        print("resume")
        self.__flag.set()

    def stop(self):
        print("stop")
        self.__flag.clear()
        self.__running.clear()
        self.raise_exception()
        self.stopped = True

    def get_lock(self):
        return self.lock

    def get_arg_info(self):
        return self._args

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(StopThreadError))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')