import os
from asyncio.exceptions import TimeoutError

from telethon.errors.rpcerrorlist import YouBlockedUserError

from userbot import CMD_HELP, TEMP_DOWNLOAD_DIRECTORY, bot
from userbot.events import register


@register(outgoing=True, pattern=r"^\.df(:? |$)([1-8])?")
async def _(fry):
    await fry.edit("**Em processamento...**")
    level = fry.pattern_match.group(2)
    if fry.fwd_from:
        return

    if not fry.reply_to_msg_id:
        return await fry.edit("**Responda a uma mensagem contendo uma imagem!**")

    reply_message = await fry.get_reply_message()

    if not reply_message.media:
        return await fry.edit("**Responda a uma mensagem contendo uma imagem!**")

    chat = "@image_deepfrybot"
    message_id_to_reply = fry.message.reply_to_msg_id
    try:
        async with fry.client.conversation(chat) as conv:
            try:
                msg = await conv.send_message(reply_message)

                if level:
                    m = f"/deepfry {level}"
                    msg_level = await conv.send_message(m, reply_to=msg.id)
                    r = await conv.get_response()

                response = await conv.get_response()
                """ - don't spam notif - """
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                return await fry.reply("**Desbloqueie @image_deepfrybot.**")

            if response.text.startswith("Forward"):
                await fry.edit(
                    "**Erro: Permita @image_deepfrybot em suas configurações de privacidade de encaminhamento.**"
                )
            else:
                downloaded_file_name = await fry.client.download_media(
                    response.media, TEMP_DOWNLOAD_DIRECTORY
                )
                await fry.client.send_file(
                    fry.chat_id,
                    downloaded_file_name,
                    force_document=False,
                    reply_to=message_id_to_reply,
                )
                """ - cleanup chat after completed - """
                try:
                    msg_level
                except NameError:
                    await fry.client.delete_messages(
                        conv.chat_id, [msg.id, response.id]
                    )
                else:
                    await fry.client.delete_messages(
                        conv.chat_id, [msg.id, response.id, r.id, msg_level.id]
                    )
    except TimeoutError:
        return await fry.edit("**Errr:** @image_deepfrybot **não está respondendo.**")
    await fry.delete()
    return os.remove(downloaded_file_name)


CMD_HELP.update(
    {
        "deepfry": ">`.df` ou >`.df [level(1-8)]`"
        "\n**Uso:** Frite a imagem/sticker da resposta."
        "\n@image_deepfrybot"
    }
)
