from pyrogram import Client, filters
from pyrogram.types import Message
from config import ALL_ID, ALL_TEXT


def is_original_post(message: Message):
    """Check if the message is an original post (not forwarded)"""
    return (
        message.chat.id in ALL_ID and
        not message.forward_from_chat and
        not message.forward_from
    )


async def edit_text_message(client: Client, message: Message, num: int):
    """Edit text message to add channel footer"""
    new_text = f"{message.text}\n\n{ALL_TEXT[num]}"
    try:
        await client.edit_message_text(
            chat_id=ALL_ID[num],
            message_id=message.id,
            text=new_text,
            disable_web_page_preview=True
        )
        print(f"Edited text message {message.id}")
    except Exception as e:
        print(f"Error editing text message: {e}")

async def edit_caption_message(client: Client, message: Message, num: int):
    """Edit media caption to add channel footer"""
    new_caption = (
        f"{message.caption}\n\n{ALL_TEXT[num]}"
        if message.caption
        else f"{ALL_TEXT[num]}"
    )
    try:
        await client.edit_message_caption(
            chat_id=ALL_ID[num],
            message_id=message.id,
            caption=new_caption
        )
        print(f"Edited caption for message {message.id}")
    except Exception as e:
        print(f"Error editing caption: {e}")