from __future__ import print_function


from threading import Timer


def hello():
    print("Hello World!")


class RepeatingTimer(object):

    def __init__(self, interval, f, *args, **kwargs):
        self.interval = interval
        self.f = f
        self.args = args
        self.kwargs = kwargs
        self.int = 0

        self.timer = None

    def callback(self):
        self.f(*self.args, **self.kwargs)
        self.start()
        print(self.int)
        self.int = self.int +1

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.timer = Timer(self.interval, self.callback)
        self.timer.start()


t = RepeatingTimer(3, hello)
t.start()
print("nigga")