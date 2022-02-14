from dggbot.message import Message
from helpers import CustomBot, RepeatTimer
from os import getenv
from pathlib import Path
from random import randint
from time import sleep
import logging
import json
import re

with Path(__file__).with_name("info.json").open("r") as f:
    json_info = json.loads(f.read())

dggbot = CustomBot(
    auth_token=getenv("DGG_AUTH"),
    username="ten71",
    owner="tena",
    last_message=json_info["last_message"],
    qd_record=json_info["quickdraw_stats"]["record_time"],
    qd_rec_holder=json_info["quickdraw_stats"]["record_holder"],
    social_credit=json_info["social_credit"],
)

qd_timer = RepeatTimer(randint(18000, 25200), dggbot.start_quickdraw)
qd_timer.start()


def is_admin(msg: Message):
    return msg.nick in ("tena", "Fritz", "RightToBearArmsLOL", "Cake", "Destiny")


def is_enabled(bot: CustomBot):
    return bot.enabled


@dggbot.event("on_broadcast")
def on_broadcast(msg):
    if msg.data == "Destiny is live! AngelThump":
        dggbot.enabled = False
        dggbot.queue_send("Disabled!")
    elif msg.data == "Destiny is offline... I enjoyed my stay. dggL":
        dggbot.enabled = True
        dggbot.queue_send("Enabled!")


@dggbot.event("on_msg")
@dggbot.event("on_privmsg")
def end_qd(msg):
    if dggbot.quickdraw["waiting"] and msg.data in ("YEEHAW", "PARDNER"):
        dggbot.end_quickdraw(msg)


@dggbot.event("on_msg")
@dggbot.event("on_privmsg")
def send_loaded_msg(msg):
    if dggbot.loaded_message and is_admin(msg) and msg.data == dggbot.loaded_message:
        dggbot.queue_send(dggbot.loaded_message)
        dggbot.loaded_message = False


@dggbot.event("on_msg")
@dggbot.event("on_privmsg")
def nextchatter_reply(msg):
    if "next chatter" in msg.data.lower() and not dggbot.cooldowns["nextchatter"]:
        dggbot.queue_send(f"> {msg.nick} no u GIGACHAD")
        dggbot.start_cooldown("nextchatter", 9000)


@dggbot.event("on_msg")
@dggbot.event("on_privmsg")
def update_social_credit(msg):
    if msg.nick in ("tng69", "ten71"):
        pattern = re.compile("(.*) (\\+|\\-)(69|100|1000|10000000)")
        if pattern.fullmatch(msg.data):
            user, amount = msg.data.split(maxsplit=1)
            try:
                amount = int(amount)
            except ValueError:
                logging.warning(f"Social credit amount '{amount}' was an invalid type")
                return
            if user not in dggbot.social_credit.keys():
                dggbot.social_credit[user] = 0
            dggbot.social_credit[user] += amount
            dggbot.write_to_info()


@dggbot.event("on_mention")
def yump(msg):
    if "MiyanoHype" in msg.data and not dggbot.cooldowns["yump"]:
        dggbot.queue_send(f"{msg.nick} MiyanoHype")
        dggbot.start_cooldown("yump")


@dggbot.command(["obamna"])
def obamna_command(msg):
    if not dggbot.cooldowns["obamna"]:
        dggbot.queue_send("obamna")
        dggbot.start_cooldown("obamna", 600)


@dggbot.command(["creditcheck", "cc"])
def creditcheck_command(msg):
    if not dggbot.cooldowns["creditcheck"]:
        if " " in msg.data:
            name = msg.data.split(maxsplit=1)[1]
        else:
            name = msg.nick
        if name in dggbot.social_credit.keys():
            dggbot.queue_send(
                f"{name}'s social credit score is: {dggbot.social_credit[name]} BINGQILIN",
            )
        else:
            dggbot.queue_send(f"{name} has no social credit history MMMM")
        dggbot.start_cooldown("creditcheck", 60)


@dggbot.command(["quickdraw", "qd"])
@dggbot.check(is_admin)
def qd_command(msg):
    dggbot.start_quickdraw()


@dggbot.command(["send", "s"])
@dggbot.check(is_admin)
def test(msg):
    dggbot.queue_send(msg.data.split(maxsplit=1)[1])


@dggbot.command(["load"])
@dggbot.check(is_admin)
def load_command(msg):
    dggbot.send_privmsg(msg.nick, f"{msg.data.split(maxsplit=1)[1]} loaded")
    dggbot.loaded_message = msg.data.split(maxsplit=1)[1]


@dggbot.command(["disable"])
@dggbot.check(is_admin)
def disable_command(msg):
    dggbot.enabled = False
    msg.reply("Disabled!")


@dggbot.command(["enable"])
@dggbot.check(is_admin)
def enable_command(msg):
    dggbot.enabled = True
    msg.reply("Enabled!")


@dggbot.command(["loglevel"])
@dggbot.check(is_admin)
def loglevel_command(msg):
    lvl = logging.getLevelName(msg.data.split(" ")[1].upper())
    if isinstance(lvl, int):
        logging.basicConfig(force=True, level=lvl)
        dggbot.send_privmsg(msg.nick, f"Logging level set to {lvl}")
    else:
        dggbot.send_privmsg(msg.nick, f"{lvl} is not a valid logging level")


@dggbot.command(["endcooldown", "endcd"])
@dggbot.check(is_admin)
def end_cooldown_command(msg):
    cd_key = msg.data.split(maxsplit=1)[1]
    if cd_key in dggbot.cooldowns:
        dggbot.cooldowns[cd_key] = False
        dggbot.send_privmsg(msg.nick, f"Ended cooldown for {cd_key}")
    else:
        dggbot.send_privmsg(msg.nick, f'No cooldown named "{cd_key}"')


@dggbot.command(["cd"])
@dggbot.check(is_admin)
def countdown_command(msg):
    message = msg.data[4:].split(" , ")[0] if " , " in msg.data else msg.data[4:]
    seconds = int(msg.data[4:].split(" , ")[1]) if " , " in msg.data else 3
    for second in reversed(range(seconds)):
        dggbot.queue_send(f"> {message} in {second + 1}")
        sleep(2 if seconds < 5 else 2.5)


while True:
    dggbot.run()
    sleep(5)
