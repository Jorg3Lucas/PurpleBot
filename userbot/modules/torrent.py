# Copyright (C) 2020 GengKapak and AnggaR96s.
# All rights reserved.

import json
import os

import requests

from userbot import CMD_HELP, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register


@register(outgoing=True, pattern=r"^\.ts(?: |$)(.*)")
async def torrent(event):
    await event.edit("**Procurando...**")
    query = event.pattern_match.group(1)
    response = requests.get(f"https://api.sumanjay.cf/torrent/?query={query}")
    try:
        ts = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        return await event.edit("**Erro: API está inativa agora, tente novamente mais tarde.**")
    if ts != response.json():
        return await event.edit("**Erro: API está inativa agora, tente novamente mais tarde.**")
    listdata = ""
    run = 0
    while True:
        try:
            run += 1
            r1 = ts[run]
            list1 = "<-----{}----->\nName: {}\nSeeders: {}\nSize: {}\nAge: {}\n<--Magnet Below-->\n{}\n\n\n".format(
                run, r1["name"], r1["seeder"], r1["size"], r1["age"], r1["magnet"]
            )
            listdata += list1
        except BaseException:
            break

    if not listdata:
        return await event.edit("**Erro: Nenhum resultado encontrado.**")

    await event.edit("**Enviando resultados...**")
    tsfileloc = f"{TEMP_DOWNLOAD_DIRECTORY}{query}.txt"
    with open(tsfileloc, "w+", encoding="utf8") as out_file:
        out_file.write(str(listdata))
    caption = f"Torrents para: `{query}`"
    await event.client.send_file(
        event.chat_id, tsfileloc, caption=caption, force_document=False
    )
    os.remove(tsfileloc)
    await event.delete()


CMD_HELP.update(
    {"torrent": ">`.ts` <consulta>" "\n**Uso:** Pesquisa por torrents de determinada consulta"}
)
