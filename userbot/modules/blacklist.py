# Copyright (C) 2021 KenHV

from sqlalchemy.exc import IntegrityError

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.blacklist (.*)")
async def blacklist(event):
    """Adds given chat to blacklist."""
    try:
        from userbot.modules.sql_helper.blacklist_sql import add_blacklist
    except IntegrityError:
        return await event.edit("**Executando em modo não SQL!**")

    group_id = event.pattern_match.group(1)
    if not group_id:
        return await event.edit("**Forneça um ID de bate-papo para a lista negra!**")

    try:
        await event.client.get_entity(int(group_id))
    except (TypeError, ValueError):
        return await event.edit("**Erro: ID inválido fornecido.**")

    try:
        add_blacklist(group_id)
    except IntegrityError:
        return await event.edit("**O bate-papo já está na lista negra.**")

    await event.edit("** Bate-papo dado na lista negra!**")


@register(outgoing=True, pattern=r"^\.unblacklist (.*)")
async def unblacklist(event):
    """Unblacklists given chat."""
    try:
        from userbot.modules.sql_helper.blacklist_sql import (
            del_blacklist,
            get_blacklist,
        )
    except IntegrityError:
        return await event.edit("**Executando em modo não SQL!**")

    group_id = event.pattern_match.group(1)
    if not group_id:
        return await event.edit("**Forneça um ID de bate-papo para remover da lista negra!**")

    if group_id == "all":
        from userbot.modules.sql_helper.blacklist_sql import del_blacklist_all

        del_blacklist_all()
        return await event.edit("**Apagadas todas as listas negras!**")

    id_exists = False
    for i in get_blacklist():
        if group_id == i.chat_id:
            id_exists = True

    if not id_exists:
        return await event.edit("**Nada para fazer.**")

    del_blacklist(group_id)
    await event.edit("**Bate-papo removido da lista negra!**")


@register(outgoing=True, pattern=r"^\.blacklists$")
async def list_blacklist(event):
    """Lists all blacklisted chats."""
    try:
        from userbot.modules.sql_helper.blacklist_sql import get_blacklist
    except IntegrityError:
        return await event.edit("**Executando em modo não SQL!**")

    chat_list = get_blacklist()
    if not chat_list:
        return await event.edit("**Você ainda não colocou nenhum bate-papo na lista negra!**")

    msg = "**Bate-papos na lista negra:**\n\n"

    for i in chat_list:
        try:
            chat = await event.client.get_entity(int(i.chat_id))
            chat = f"{chat.title} | `{i.chat_id}`"
        except (TypeError, ValueError):
            chat = f"__Não foi possível buscar informações do bate-papo__ | `{i.chat_id}`"

        msg += f"• {chat}\n"

    await event.edit(msg)


CMD_HELP.update(
    {
        "blacklist": "**Desativa todas as funções do userbot em grupos da lista negra.**"
        "\n\n`>.blacklist <chat id>`"
        "\n**Uso:** Bota o chat na lista negra."
        "\n\n>`.unblacklist <chat id>`"
        "\n**Uso:** Remove o bate-papo da lista negra."
        "\n\n>`.unblacklist all`"
        "\n**Uso:** Remove todos os chats da lista negra."
        "\n\n>`.blacklists`"
        "\n**Uso:** Lista todos os bate-papos na lista negra."
    }
)
