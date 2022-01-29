from dggbot import DGGBot
from dggbot.message import Message
from os import getenv
from datetime import datetime
from threading import Timer
import logging
import time


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Bot(DGGBot):
    admins = ('tena', 'Fritz', 'RightToBearArmsLOL', 'Cake', 'Destiny')

    def __init__(self, auth_token=None, username=None, prefix='!'):
        super().__init__(auth_token=auth_token, username=username, prefix=prefix)
        self.last_message = {"content": None, "time": None}
        self.quickdraw = {"waiting": False, "time_started": None,
                          "record_time": None, "record_holder": None}

    def on_command(self, msg: Message):
        cmd = msg.data.split(' ')[0][1:]
        if cmd in self._commands and msg.nick in self.admins:
            self._commands[cmd](msg)

    def on_broadcast(self, msg):
        if msg.data == "Destiny is live! AngelThump":
            self.enabled = False
        elif msg.data == 'Destiny is offline... I enjoyed my stay. dggL':
            self.enabled = True

    def on_msg(self, msg):
        if self.is_command(msg):
            self.on_command(msg)
        if (self.quickdraw["waiting"] and
           msg.data in ["YEEHAW", "PARDNER"]):
            self.end_quickdraw(msg)

    def queue_send(self, message: str):
        current_time = datetime.now()
        if message == self.last_message["content"]:
            message += " ."
        if (current_time - self.last_message["time"]).total_seconds < 1:
            sleep(1)
        self.send(message)
        self.last_message["content"] = message
        self.last_message["time"] = current_time

    def start_quickdraw(self):
        if self.enabled:
            self.queue_send(".")
            self.quickdraw["waiting"] = True
            self.quickdraw["time_started"] = datetime.now()

    def end_quickdraw(self, msg):
        delta = datetime.now() - self.quickdraw["time_started"]
        response_time = round(delta.total_seconds(), 2)
        self.queue_send(response_time)


dggbot = Bot(getenv("DGG_AUTH"), username="ten71")


@dggbot.mention()
def yump(msg):
    if "MiyanoHype" in msg.data:
        dggbot.send(f'{msg.nick} MiyanoHype')


@dggbot.command("qd")
def quickdraw():
    dggbot.start_quickdraw()

while True:
    dggbot.run()
    time.sleep(5)
