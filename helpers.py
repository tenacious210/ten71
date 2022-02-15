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


class CustomBot(DGGBot):
    def __init__(
        self,
        auth_token,
        username,
        owner,
        qd_record,
        qd_rec_holder,
        social_credit,
        prefix="!",
    ):
        super().__init__(
            auth_token=auth_token, username=username, prefix=prefix, owner=owner
        )
        self.enabled = True
        self.loaded_message = False
        self.cooldowns = {
            "yump": False,
            "nextchatter": False,
            "obamna": False,
            "creditcheck": False,
        }
        self.last_message = {"content": "", "time": datetime.now()}
        self.quickdraw = {
            "time_started": datetime.now(),
            "waiting": False,
            "record_time": qd_record,
            "record_holder": qd_rec_holder,
        }
        self.social_credit = social_credit

    def queue_send(self, payload: str, pm_nick=False):
        current_time = datetime.now()
        if payload == self.last_message["content"]:
            payload += " ."
        if (current_time - self.last_message["time"]).total_seconds() < 1:
            time.sleep(1)
        if pm_nick:
            self.send_privmsg(pm_nick, payload)
        else:
            self.send(payload)
        self.last_message["content"] = payload
        self.last_message["time"] = current_time

    def start_quickdraw(self, *args):
        if self.enabled:
            self.queue_send("> QUICKDRAW! PARDNER vs YEEHAW")
            self.quickdraw["waiting"] = True
            self.quickdraw["time_started"] = datetime.now()
        return

    def end_quickdraw(self, msg: Message):
        self.quickdraw["waiting"] = False
        delta = datetime.now() - self.quickdraw["time_started"]
        response_time = round(delta.total_seconds(), 2)
        ending_message = f"{msg.data} {msg.nick} shot first! Response time: {response_time} seconds. "
        if response_time < self.quickdraw["record_time"]:
            ending_message += "New record!"
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

    def write_to_qd(self):
        qd_dict = {
            "record_time": self.quickdraw["record_time"],
            "record_holder": self.quickdraw["record_holder"],
        }
        qd_file = Path(__file__).with_name("quickdraw.json")
        with qd_file.open("w") as qd:
            json.dump(qd_dict, qd)
        return

    def write_to_sc(self):
        sc_file = Path(__file__).with_name("social_credit.json")
        with sc_file.open("w") as sc:
            json.dump(self.social_credit, sc)
