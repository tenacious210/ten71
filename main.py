from dggbot.message import Message, PrivateMessage
from helpers import CustomBot, RepeatTimer
from os import getenv
from pathlib import Path
from random import randint
from time import sleep
import logging
import json


with Path(__file__).with_name('info.json').open('r') as f:
    json_info = json.loads(f.read())

dggbot = CustomBot(auth_token=getenv("DGG_AUTH"),
                   username="ten71", owner="tena", last_message=json_info["last_message"],
                   qd_record=json_info["quickdraw_stats"]["record_time"],
                   qd_rec_holder=json_info["quickdraw_stats"]["record_holder"])

qd_timer = RepeatTimer(randint(18000, 25200), dggbot.start_quickdraw)
qd_timer.start()


def is_admin(msg: Message):
    return msg.nick in ('tena', 'Fritz', 'RightToBearArmsLOL', 'Cake', 'Destiny')


def is_enabled(bot: CustomBot):
    return bot.enabled


@dggbot.event("on_broadcast")
def on_broadcast(msg):
    if msg.data == "Destiny is live! AngelThump":
        dggbot.enabled = False
        dggbot.queue_send("Disabled!")
    elif msg.data == 'Destiny is offline... I enjoyed my stay. dggL':
        dggbot.enabled = True
        dggbot.queue_send("Enabled!")


@dggbot.event("on_msg")
def end_qd(msg):
    if (dggbot.quickdraw["waiting"] and msg.data in ("YEEHAW", "PARDNER")):
        dggbot.end_quickdraw(msg)


@dggbot.mention()
def yump(msg):
    if "MiyanoHype" in msg.data and dggbot.cooldowns["yump"] is False:
        if isinstance(msg, PrivateMessage):
            dggbot.send_privmsg(msg.nick, f'{msg.nick} MiyanoHype')
        else:
            dggbot.queue_send(f'{msg.nick} MiyanoHype')
        dggbot.start_cooldown("yump")


@dggbot.command(["quickdraw", "qd"])
@dggbot.check(is_admin)
def qd_command(msg):
    dggbot.start_quickdraw()


@dggbot.command(["send", "s"])
@dggbot.check(is_admin)
def test(msg):
    dggbot.queue_send(msg.data[6:])


@dggbot.command(["load"])
@dggbot.check(is_admin)
def load_command(msg):
    dggbot.send_privmsg(msg.nick, f'{msg.data[6:]} loaded')
    dggbot.loaded_message = msg.data[6:]


@dggbot.command(["disable"])
@dggbot.check(is_admin)
def disable_command(msg):
    dggbot.enabled = False
    if isinstance(msg, PrivateMessage):
        dggbot.send_privmsg(msg.nick, "Disabled!")
    else:
        dggbot.queue_send("Disabled!")


@dggbot.command(["enable"])
@dggbot.check(is_admin)
def enable_command(msg):
    dggbot.enabled = True
    if isinstance(msg, PrivateMessage):
        dggbot.send_privmsg(msg.nick, "Enabled!")
    else:
        dggbot.queue_send("Enabled!")


@dggbot.command(["loglevel"])
@dggbot.check(is_admin)
def set_debug_level(msg):
    lvl = msg.data.split(' ')[1]
    if lvl.upper() in ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logging.basicConfig(force=True, level=lvl.upper())
        dggbot.send_privmsg(msg.nick, f'Logging level set to {lvl}')
    else:
        dggbot.send_privmsg(msg.nick, f'{lvl} is not a valid logging level')


@dggbot.command(["endcd"])
@dggbot.check(is_admin)
def end_cd(msg):
    cd_key = msg.data[7:]
    if cd_key in dggbot.cooldowns:
        dggbot.cooldowns[cd_key] = False
        dggbot.send_privmsg(msg.nick, f"Ended cooldown for {cd_key}")
    else:
        dggbot.send_privmsg(msg.nick, f'No cooldown named "{cd_key}"')


@dggbot.command(["countdown", "cd"])
@dggbot.check(is_admin)
def countdown_command(msg, seconds=5):
    message, seconds = msg.data[4:].split(' , ')
    for second in reversed(range(seconds)):
        dggbot.queue_send(f'> {message} in {second}')


while True:
    dggbot.run()
    sleep(5)
