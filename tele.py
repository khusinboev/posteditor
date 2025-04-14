from telethon import TelegramClient, events
from config import API_ID, API_HASH, SESSION_NAME, ALL_ID, ALL_TEXT, entities_right

# Client yaratamiz
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


from telethon.tl.types import MessageEntityCustomEmoji

def get_premium_emojis(message):
    entities = []

    try:
        if message.entities:
            entities.extend(message.entities)
    except AttributeError:
        pass

    try:
        if message.caption_entities:
            entities.extend(message.caption_entities)
    except AttributeError:
        pass

    return entities

def is_original_post(event):
    """Check if the message is an original post (not forwarded)"""
    print("tekshiruv")
    return (
            event.chat and
            event.chat.username in ALL_ID and
            not event.fwd_from
    )


async def edit_text_message(event, num: int):
    print("tahrir1")
    """Edit text message to add channel footer"""
    new_text = f"{event.text}\n\n{ALL_TEXT[num]}"
    # try:
    await client.edit_message(
        entity=ALL_ID[num],
        message=event.id,
        text=new_text,
        link_preview=False,
        formatting_entities=get_premium_emojis(event.message)+entities_right(event.text, num),
        parse_mode='markdown'
    )
    print(f"Edited text message {event.id}")
    # except Exception as e:
    #     print(f"Error editing text message: {e}")


async def edit_caption_message(event, num: int):
    caption = event.message.message if event.message else ""
    new_caption = f"{caption}\n\n{ALL_TEXT[num]}" if caption else ALL_TEXT[num]
    try:
        await client.edit_message(
            entity=ALL_ID[num],
            message=event.id,
            text=new_caption,
            link_preview=False,
            formatting_entities=get_premium_emojis(event.message)+entities_right(event.text, num),
            parse_mode='markdown'
        )
    except Exception as e:
        print(f"Error editing caption: {e}")


@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    print("girish")
    username = event.chat.username if event.chat else None
    print(username)
    with open("data.txt", "r", encoding='utf-8') as file:
        content = file.read()
    print(content)

    if username and is_original_post(event) and content == "/start":
        num = ALL_ID.index(username)
        if event.text:
            await edit_text_message(event, num)
        elif event.message.media and not event.text:
            await edit_caption_message(event, num)

@client.on(events.NewMessage())
async def handle_all(event):
    print("bedaquuu")

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    client.start()
    client.run_until_disconnected()
