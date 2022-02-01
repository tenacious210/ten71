from dggbot.message import PrivateMessage
from helpers import Bot, RepeatTimer
from os import getenv
from pathlib import Path
from random import randint
from time import sleep
import logging
import json


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
    if "MiyanoHype" in msg.data and dggbot.cooldowns["yump"] is False:
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


@dggbot.command("load")
def load(msg):
    dggbot.send_privmsg(msg.nick, f'{msg.data[6:]} loaded')
    dggbot.loaded_message = msg.data[6:]


@dggbot.command("ten71disable")
def disable(msg):
    dggbot.enabled = False
    if isinstance(msg, PrivateMessage):
        dggbot.send_privmsg(msg.nick, "Disabled!")
    else:
        dggbot.queue_send("Disabled!")


@dggbot.command("ten71enable")
def enable(msg):
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


while True:
    dggbot.run()
    sleep(5)
