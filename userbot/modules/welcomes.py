from telethon.events import ChatAction

from userbot import BOTLOG_CHATID, CLEAN_WELCOME, CMD_HELP, LOGS, bot
from userbot.events import register


@bot.on(ChatAction)
async def welcome_to_chat(event):
    try:
        from userbot.modules.sql_helper.welcome_sql import (
            get_current_welcome_settings,
            update_previous_welcome,
        )
    except AttributeError:
        return
    cws = get_current_welcome_settings(event.chat_id)
    if cws:
        """user_added=True,
        user_joined=True,
        user_left=False,
        user_kicked=False"""
        if (event.user_joined or event.user_added) and not (await event.get_user()).bot:
            if CLEAN_WELCOME:
                try:
                    await event.client.delete_messages(
                        event.chat_id, cws.previous_welcome
                    )
                except Exception as e:
                    LOGS.warning(str(e))
            a_user = await event.get_user()
            chat = await event.get_chat()
            me = await event.client.get_me()

            title = chat.title or "este chat"
            participants = await event.client.get_participants(chat)
            count = len(participants)
            mention = f"[{a_user.first_name}](tg://user?id={a_user.id})"
            my_mention = f"[{me.first_name}](tg://user?id={me.id})"
            first = a_user.first_name
            last = a_user.last_name
            fullname = f"{first} {last}" if last else first
            username = f"@{a_user.username}" if a_user.username else mention
            userid = a_user.id
            my_first = me.first_name
            my_last = me.last_name
            my_fullname = f"{my_first} {my_last}" if my_last else my_first
            my_username = f"@{me.username}" if me.username else my_mention
            file_media = None
            current_saved_welcome_message = None
            if cws:
                if cws.f_mesg_id:
                    msg_o = await event.client.get_messages(
                        entity=BOTLOG_CHATID, ids=int(cws.f_mesg_id)
                    )
                    file_media = msg_o.media
                    current_saved_welcome_message = msg_o.message
                elif cws.reply:
                    current_saved_welcome_message = cws.reply
            current_message = await event.reply(
                current_saved_welcome_message.format(
                    mention=mention,
                    title=title,
                    count=count,
                    first=first,
                    last=last,
                    fullname=fullname,
                    username=username,
                    userid=userid,
                    my_first=my_first,
                    my_last=my_last,
                    my_fullname=my_fullname,
                    my_username=my_username,
                    my_mention=my_mention,
                ),
                file=file_media,
            )
            update_previous_welcome(event.chat_id, current_message.id)


@register(outgoing=True, pattern=r"^\.setwelcome(?: |$)(.*)")
async def save_welcome(event):
    try:
        from userbot.modules.sql_helper.welcome_sql import add_welcome_setting
    except AttributeError:
        return await event.edit("**Executando em modo não SQL!**")
    msg = await event.get_reply_message()
    string = event.pattern_match.group(1)
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG_CHATID:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#WELCOME_NOTE \nCHAT ID: {event.chat_id}"
                "\nA mensagem a seguir é salva como a nova nota de boas-vindas "
                "para o chat, por favor NÃO o exclua!",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID, messages=msg, from_peer=event.chat_id, silent=True
            )
            msg_id = msg_o.id
        else:
            return await event.edit(
                "**Salvar mídia como parte da nota de boas-vindas requer que BOTLOG_CHATID seja definido.**"
            )
    elif event.reply_to_msg_id and not string:
        rep_msg = await event.get_reply_message()
        string = rep_msg.text
    success = "**Nota de boas vindas {} para este chat.**"
    if add_welcome_setting(event.chat_id, 0, string, msg_id) is True:
        await event.edit(success.format("salva"))
    else:
        await event.edit(success.format("atualizada"))


@register(outgoing=True, pattern=r"^\.checkwelcome$")
async def show_welcome(event):
    try:
        from userbot.modules.sql_helper.welcome_sql import get_current_welcome_settings
    except AttributeError:
        return await event.edit("**Executando em modo não SQL!**")
    cws = get_current_welcome_settings(event.chat_id)
    if not cws:
        return await event.edit("**Nenhuma mensagem de boas-vindas salva aqui.**")
    if cws.f_mesg_id:
        msg_o = await event.client.get_messages(
            entity=BOTLOG_CHATID, ids=int(cws.f_mesg_id)
        )
        await event.edit(
            "**No momento, estou dando as boas-vindas a novos usuários com esta nota de boas-vindas.**"
        )
        await event.reply(msg_o.message, file=msg_o.media)
    elif cws.reply:
        await event.edit(
            "**No momento, estou dando as boas-vindas a novos usuários com esta nota de boas-vindas.**"
        )
        await event.reply(cws.reply)


@register(outgoing=True, pattern=r"^\.rmwelcome$")
async def del_welcome(event):
    try:
        from userbot.modules.sql_helper.welcome_sql import rm_welcome_setting
    except AttributeError:
        return await event.edit("**Executando em modo não SQL!**")
    if rm_welcome_setting(event.chat_id) is True:
        await event.edit("**Nota de boas-vindas excluída deste bate-papo.**")
    else:
        await event.edit("**Não acho que eu tenha uma nota de boas-vindas aqui?**")


CMD_HELP.update(
    {
        "welcome": ">`.setwelcome <mensagem de boas-vindas> ou responda a uma mensagem com .setwelcome`"
        "\n**Uso:** Salva a mensagem como nota de boas-vindas no chat."
        "\n\nVariáveis disponíveis para formatar mensagens de boas-vindas :"
        "\n`{mention}, {title}, {count}, {first}, {last}, {fullname}, "
        "{userid}, {username}, {my_first}, {my_fullname}, {my_last}, "
        "{my_mention}, {my_username}`"
        "\n\n>`.checkwelcome`"
        "\n**Uso:** Verifique se você tem uma nota de boas-vindas no chat."
        "\n\n>`.rmwelcome`"
        "\n**Uso:** Exclui a nota de boas-vindas do bate-papo atual."
    }
)
