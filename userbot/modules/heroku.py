# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
   Heroku manager for your userbot
"""

import math
import os

import aiohttp
import heroku3

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, HEROKU_API_KEY, HEROKU_APP_NAME
from userbot.events import register

heroku_api = "https://api.heroku.com"
if HEROKU_APP_NAME is not None and HEROKU_API_KEY is not None:
    Heroku = heroku3.from_key(HEROKU_API_KEY)
    app = Heroku.app(HEROKU_APP_NAME)
    heroku_var = app.config()
else:
    app = None
"""
   ConfigVars setting, get current var, set var or delete var...
"""


@register(outgoing=True, pattern=r"^\.(get|del) var(?: |$)(\w*)")
async def variable(var):
    exe = var.pattern_match.group(1)
    if app is None:
        await var.edit(
            "**Por favor configure seu** `HEROKU_APP_NAME` **e** `HEROKU_API_KEY`**.**"
        )
        return False
    await var.edit("**Em processamento...**")
    variable = var.pattern_match.group(2)
    if exe == "get":
        if variable != "":
            if variable in heroku_var:
                if BOTLOG:
                    await var.client.send_message(
                        BOTLOG_CHATID,
                        "#CONFIGVAR\n\n"
                        "**ConfigVar**:\n"
                        f"`{variable}` = `{heroku_var[variable]}`\n",
                    )
                    await var.edit("**Verifique o seu grupo de botlog.**")
                    return True
                await var.edit("**Habilite** `BOTLOG`**!**")
                return False
            await var.edit("**Erro: ConfigVar não encontrado.**")
            return True
        else:
            configvars = heroku_var.to_dict()
            if BOTLOG:
                msg = "".join(
                    f"`{item}` = `{configvars[item]}`\n" for item in configvars
                )
                await var.client.send_message(
                    BOTLOG_CHATID, "#CONFIGVARS\n\n" "**ConfigVars**:\n" f"{msg}"
                )
                await var.edit("**Verifique o seu grupo de botlog.**")
                return True
            await var.edit("**Habilite** `BOTLOG`**!**")
            return False
    elif exe == "del":
        if variable == "":
            await var.edit("**Erro: Dê-me um ConfigVar para excluir!**")
            return False
        if variable in heroku_var:
            if BOTLOG:
                await var.client.send_message(
                    BOTLOG_CHATID,
                    "#DELCONFIGVAR\n\n" "**Excluir ConfigVar**:\n" f"`{variable}`",
                )
            await var.edit("**Deleted ConfigVar.**")
            del heroku_var[variable]
        else:
            await var.edit("**Erro: ConfigVar não encontrado.**")
            return True


@register(outgoing=True, pattern=r"^\.set var (\w*) ([\s\S]*)")
async def set_var(var):
    if app is None:
        return await var.edit(
            "**Por favor configure seu** `HEROKU_APP_NAME` **e** `HEROKU_API_KEY`**.**"
        )
    await var.edit("**Configurando ConfigVar...**")
    variable = var.pattern_match.group(1)
    value = var.pattern_match.group(2)
    if BOTLOG:
        if variable in heroku_var:
            await var.client.send_message(
                BOTLOG_CHATID,
                "#SETCONFIGVAR\n\n"
                "**Mudança de ConfigVar**:\n"
                f"`{variable}` = `{value}`",
            )
        else:
            await var.client.send_message(
                BOTLOG_CHATID,
                "#ADDCONFIGVAR\n\n" "**Adicionada ConfigVar**:\n" f"`{variable}` = `{value}`",
            )
    await var.edit("**ConfigVar definida com sucesso.**")
    heroku_var[variable] = value


"""
    Check account quota, remaining quota, used quota, used app quota
"""


@register(outgoing=True, pattern=r"^\.usage$")
async def dyno_usage(dyno):
    """
    Get your account Dyno Usage
    """
    if app is None:
        return await dyno.edit(
            "** Configure o seu** `HEROKU_APP_NAME` **e** `HEROKU_API_KEY`**.**"
        )
    await dyno.edit("**Em processamento...**")
    user_id = Heroku.account().id
    path = "/accounts/" + user_id + "/actions/get-quota"
    async with aiohttp.ClientSession() as session:
        useragent = (
            "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/81.0.4044.117 Mobile Safari/537.36"
        )
        headers = {
            "User-Agent": useragent,
            "Authorization": f"Bearer {HEROKU_API_KEY}",
            "Accept": "application/vnd.heroku+json; version=3.account-quotas",
        }
        async with session.get(heroku_api + path, headers=headers) as r:
            if r.status != 200:
                await dyno.client.send_message(
                    dyno.chat_id, f"`{r.reason}`", reply_to=dyno.id
                )
                await dyno.edit("**Erro: Heroku está sendo Heroku.**")
                return False
            result = await r.json()
            quota = result["account_quota"]
            quota_used = result["quota_used"]
            """ - User Quota Limit and Used - """
            remaining_quota = quota - quota_used
            percentage = math.floor(remaining_quota / quota * 100)
            minutes_remaining = remaining_quota / 60
            hours = math.floor(minutes_remaining / 60)
            minutes = math.floor(minutes_remaining % 60)
            """ - User App Used Quota - """
            Apps = result["apps"]
            for apps in Apps:
                if apps.get("app_uuid") == app.id:
                    AppQuotaUsed = apps.get("quota_used") / 60
                    AppPercentage = math.floor(apps.get("quota_used") * 100 / quota)
                    break
            else:
                AppQuotaUsed = 0
                AppPercentage = 0

            AppHours = math.floor(AppQuotaUsed / 60)
            AppMinutes = math.floor(AppQuotaUsed % 60)

            await dyno.edit(
                "**Estatísticas de horas do dinamômetro Heroku para o mês atual**\n\n"
                f"**Uso ({app.name}):** {AppHours} hour(s), {AppMinutes} minute(s) - {AppPercentage}%\n"
                f"**Remanescente (total):** {hours} hour(s), {minutes} minute(s) - {percentage}%"
            )
            return True


@register(outgoing=True, pattern=r"^\.logs")
async def _(dyno):
    if app is None:
        return await dyno.edit(
            "**Por favor configure seu** `HEROKU_APP_NAME` **e** `HEROKU_API_KEY`**.**"
        )
    await dyno.edit("**Em processamento...**")
    with open("logs.txt", "w") as log:
        log.write(app.get_log())
    await dyno.client.send_file(
        entity=dyno.chat_id, file="logs.txt", caption="**Logs do dinamômetro Heroku**"
    )
    await dyno.delete()
    return os.remove("logs.txt")


CMD_HELP.update(
    {
        "heroku": ">.`usage`"
        "\n**Uso:** Mostra estatísticas de hora do dinamômetro do Heroku."
        "\n\n>`.set var <configvar> <value>`"
        "\n**Uso:** Adiciona um novo ConfigVar ou atualiza o ConfigVar existente."
        "\nO bot irá reiniciar após usar este comando."
        "\n\n>`.get var <configvar>[opcional]`"
        "\n**Uso:** Mostra os valores atuais para o especificado ou todos os ConfigVars."
        "\nCertifique-se de executar o comando em um grupo privado se você não tiver o Botlog configurado."
        "\n\n>`.del var <configvar>`"
        "\n**Uso:** Remove o ConfigVar especificado."
        "\nO bot irá reiniciar após usar este comando."
        "\n\n>`.logs`"
        "\n**Uso:** Recupera registros do dinamômetro do Heroku."
    }
)
