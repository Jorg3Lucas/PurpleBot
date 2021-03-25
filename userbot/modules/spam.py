# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.

import asyncio
from asyncio import sleep

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.cspam (.+)")
async def tmeme(e):
    cspam = str(e.pattern_match.group(1))
    message = cspam.replace(" ", "")
    await e.delete()
    for letter in message:
        await e.respond(letter)


@register(outgoing=True, pattern=r"^\.wspam (.+)")
async def t_meme(e):
    wspam = str(e.pattern_match.group(1))
    message = wspam.split()
    await e.delete()
    for word in message:
        await e.respond(word)


@register(outgoing=True, pattern=r"^\.spam (\d+) (.+)")
async def spammers(e):
    counter = int(e.pattern_match.group(1))
    spam_message = str(e.pattern_match.group(2))
    await e.delete()
    await asyncio.wait([e.respond(spam_message) for i in range(counter)])


@register(outgoing=True, pattern=r"^\.picspam (\d+) (.+)")
async def tiny_pic_spam(e):
    counter = int(e.pattern_match.group(1))
    link = str(e.pattern_match.group(2))
    await e.delete()
    for _ in range(1, counter):
        await e.client.send_file(e.chat_id, link)


@register(outgoing=True, pattern=r"^\.delayspam (\d+) (\d+) (.+)")
async def spammer(e):
    spamDelay = float(e.pattern_match.group(1))
    counter = int(e.pattern_match.group(2))
    spam_message = str(e.pattern_match.group(3))
    await e.delete()
    for _ in range(1, counter):
        await e.respond(spam_message)
        await sleep(spamDelay)


CMD_HELP.update(
    {
        "spam": ">`.cspam <texto>`"
        "\n**Uso:** Spamma o texto letra por letra."
        "\n\n>`.spam <número> <texto>`"
        "\n**Uso:** Spamma o texto no chat!"
        "\n\n>`.wspam <texto>`"
        "\n**Uso:** Spamma o texto palavra por palavra."
        "\n\n>`.picspam <número> <link para imagem/gif>`"
        "\n**Uso:** Como se o spam de texto não fosse suficiente!"
        "\n\n>`.delayspam <atraso> <número> <texto>`"
        "\n**Uso:** .spam mas com atraso personalizado."
        "\n\n\n**NOTA: Spamme por sua própria conta e risco!**"
    }
)
