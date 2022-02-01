from dggbot import DGGBot
from datetime import datetime
from threading import Timer
from dggbot.message import Message
from pathlib import Path
import time
import json


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Bot(DGGBot):
    admins = ('tena', 'Fritz', 'RightToBearArmsLOL', 'Cake', 'Destiny')

    def __init__(self, auth_token, username, prefix='!',
                 qd_record=99.9, qd_rec_holder='ten71', last_message=''):
        super().__init__(auth_token=auth_token, username=username, prefix=prefix)
        self.enabled = True
        self.loaded_message = False
        self.cooldowns = {"yump": False, "nextchatter": False}
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
        if (self.loaded_message is not False and
           msg.data == self.loaded_message and
           msg.nick in self.admins):
            self.queue_send(self.loaded_message)
            self.loaded_message = False
        if ("next chatter" in msg.data.lower()) and self.cooldowns["nextchatter"] is False:
            self.queue_send(f'> {msg.nick} no u GIGACHAD')
            self.start_cooldown("nextchatter", 10800)

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
        self.write_to_info()

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
            self.write_to_info()
        else:
            ending_message += f'Record time: {self.quickdraw["record_time"]} by {self.quickdraw["record_holder"]}'
        self.queue_send(ending_message)

    def start_cooldown(self, key, seconds=300):
        self.cooldowns[key] = Timer(seconds, self.end_cooldown, [key])
        self.cooldowns[key].start()

    def end_cooldown(self, key):
        self.cooldowns[key] = False

    def write_to_info(self):
        info_dict = {
            "last_message": self.last_message["content"],
            "quickdraw_stats": {
                "record_time": self.quickdraw["record_time"],
                "record_holder": self.quickdraw["record_holder"]
                }
        }
        info_file = Path(__file__).with_name('info.json')
        with info_file.open('w') as info:
            json.dump(info_dict, info)
        return
