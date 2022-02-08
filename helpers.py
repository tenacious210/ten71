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
        last_message,
        prefix="!",
    ):
        super().__init__(
            auth_token=auth_token, username=username, prefix=prefix, owner=owner
        )
        self.enabled = True
        self.loaded_message = False
        self.cooldowns = {"yump": False, "nextchatter": False}
        self.last_message = {"content": last_message, "time": datetime.now()}
        self.quickdraw = {
            "time_started": datetime.now(),
            "waiting": False,
            "record_time": qd_record,
            "record_holder": qd_rec_holder,
        }

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

    def write_to_info(self):
        info_dict = {
            "last_message": self.last_message["content"],
            "quickdraw_stats": {
                "record_time": self.quickdraw["record_time"],
                "record_holder": self.quickdraw["record_holder"],
            },
        }
        info_file = Path(__file__).with_name("info.json")
        with info_file.open("w") as info:
            json.dump(info_dict, info)
        return
