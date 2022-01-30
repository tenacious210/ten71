from dggbot import DGGBot
from dggbot.message import Message, PrivateMessage
from os import getenv
from datetime import datetime
from threading import Timer
from pathlib import Path
from random import randint
import logging
import json
import time


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Bot(DGGBot):
    admins = ('tena', 'Fritz', 'RightToBearArmsLOL', 'Cake', 'Destiny')

    def __init__(self, auth_token=None, username=None, prefix='!',
                 qd_record=99.9, qd_rec_holder='ten71', last_message=''):
        super().__init__(auth_token=auth_token, username=username, prefix=prefix)
        self.enabled = True
        self.cooldowns = {"yump": False}
        self.last_message = {"content": last_message, "time": datetime.now()}
        self.quickdraw = {"time_started": datetime.now(), "waiting": False,
                          "record_time": qd_record, "record_holder": qd_rec_holder}

    def on_command(self, msg: Message):
        cmd = msg.data.split(' ')[0][1:]
        if cmd in self._commands and msg.nick in self.admins:
            self._commands[cmd](msg)

    def on_broadcast(self, msg):
        if msg.data == "Destiny is live! AngelThump":
            self.enabled = False
        elif msg.data == 'Destiny is offline... I enjoyed my stay. dggL':
            self.enabled = True

    def on_privmsg(self, msg):
        if self.is_command(msg):
            self.on_command(msg)
        if (self.quickdraw["waiting"] and
           msg.data in ["YEEHAW", "PARDNER"]):
            self.end_quickdraw(msg)

    def on_msg(self, msg: Message):
        if self.is_command(msg):
            self.on_command(msg)
        if (self.quickdraw["waiting"] and
           msg.data in ["YEEHAW", "PARDNER"]):
            self.end_quickdraw(msg)

    def queue_send(self, message: str):
        current_time = datetime.now()
        if message == self.last_message["content"]:
            message += " ."
        if (current_time - self.last_message["time"]).total_seconds() < 1:
            time.sleep(1)
        self.send(message)
        # For debugging:
        # self.send_privmsg("tena", message)
        self.last_message["content"] = message
        self.last_message["time"] = current_time

    def start_quickdraw(self, *args):
        self.queue_send("> QUICKDRAW! PARDNER vs YEEHAW")
        self.quickdraw["waiting"] = True
        self.quickdraw["time_started"] = datetime.now()

    def end_quickdraw(self, msg: Message):
        self.quickdraw["waiting"] = False
        delta = datetime.now() - self.quickdraw["time_started"]
        response_time = round(delta.total_seconds(), 2)
        ending_message = f'{msg.data} {msg.nick} shot first! Response time: {response_time} seconds. '
        if response_time < self.quickdraw["record_time"]:
            ending_message += 'New record!'
            self.quickdraw["record_time"] = response_time
            self.quickdraw["record_holder"] = msg.nick
            write_to_info(self.last_message["content"], response_time, msg.nick)
        else:
            ending_message += f'Record time: {self.quickdraw["record_time"]} by {self.quickdraw["record_holder"]}'
        self.queue_send(ending_message)

    def start_cooldown(self, key, seconds=300):
        self.cooldowns[key] = Timer(seconds, self.end_cooldown, [key])
        self.cooldowns[key].start()

    def end_cooldown(self, key):
        self.cooldowns[key] = False


with Path(__file__).with_name('info.json').open('r') as f:
    json_info = json.loads(f.read())

dggbot = Bot(getenv("DGG_AUTH"), username="ten71", last_message=json_info["last_message"],
             qd_record=json_info["quickdraw_stats"]["record_time"],
             qd_rec_holder=json_info["quickdraw_stats"]["record_holder"])

qd_timer = RepeatTimer(randint(18000, 25200),
                       dggbot.start_quickdraw if dggbot.enabled else print,
                       ["Bot disabled, not starting quickdraw."])
qd_timer.start()


@dggbot.mention()
def yump(msg):
    if ("MiyanoHype" in msg.data) and not (isinstance(dggbot.cooldowns["yump"], Timer)):
        if isinstance(msg, PrivateMessage):
            dggbot.send_privmsg(msg.nick, f'{msg.nick} MiyanoHype')
        else:
            dggbot.queue_send(f'{msg.nick} MiyanoHype')
            dggbot.start_cooldown("yump")


@dggbot.command("qd")
def quickdraw(msg):
    dggbot.start_quickdraw()


@dggbot.command("send")
def test(msg):
    dggbot.queue_send(msg.data[6:])


@dggbot.command("ten71disable")
def disable(msg):
    dggbot.enabled = False
    if isinstance(msg, PrivateMessage):
        dggbot.send_privmsg(msg.nick, "Disabled!")
    else:
        dggbot.queue_send("Disabled!")


@dggbot.command("ten71enable")
def disable(msg):
    dggbot.enabled = True
    if isinstance(msg, PrivateMessage):
        dggbot.send_privmsg(msg.nick, "Enabled!")
    else:
        dggbot.queue_send("Enabled!")


@dggbot.command("loglevel")
def set_debug_level(msg):
    lvl = msg.data.split(' ')[1]
    if lvl.upper() in ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logging.basicConfig(force=True, level=lvl.upper())
        dggbot.send_privmsg(msg.nick, f'Logging level set to {lvl}')
    else:
        dggbot.send_privmsg(msg.nick, f'{lvl} is not a valid logging level')


def write_to_info(last_message, qd_rec_time, qd_rec_holder):
    info_dict = {
        "last_message": last_message,
        "quickdraw_stats": {
            "record_time": qd_rec_time,
            "record_holder": qd_rec_holder
            }
    }
    info_file = Path(__file__).with_name('info.json')
    with info_file.open('w') as info:
        json.dump(info_dict, info)
    return


while True:
    dggbot.run()
    time.sleep(5)
