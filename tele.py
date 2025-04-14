from telethon import TelegramClient, events
from config import API_ID, API_HASH, SESSION_NAME, ALL_ID, ALL_TEXT, entities_right

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

def get_premium_emojis(message):
    """Xabardagi mavjud entity'larni qaytaradi"""
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
    return (
        event.chat and
        event.chat.username in ALL_ID and
        not event.fwd_from
    )


async def edit_text_message(event, num: int):
    try:
        original_text = event.message.message
        add_text = ALL_TEXT[num]
        new_text = f"{original_text}\n\n{add_text}"

        entities = get_premium_emojis(event.message)
        entities += entities_right(original_text, num)

        await client.edit_message(
            entity=ALL_ID[num],
            message=event.message.id,
            text=new_text,
            link_preview=False,
            formatting_entities=entities
        )
        print(f"Tahrirlandi (text): {event.message.id}")
    except Exception as e:
        print(f"Xatolik (text): {e}")


async def edit_caption_message(event, num: int):
    try:
        caption = event.message.message or ""
        add_text = ALL_TEXT[num]
        new_caption = f"{caption}\n\n{add_text}" if caption else add_text

        entities = get_premium_emojis(event.message)
        entities += entities_right(caption, num)

        await client.edit_message(
            entity=ALL_ID[num],
            message=event.message.id,
            text=new_caption,
            link_preview=False,
            formatting_entities=entities
        )
        print(f"Tahrirlandi (caption): {event.message.id}")
    except Exception as e:
        print(f"Xatolik (caption): {e}")


@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    username = event.chat.username if event.chat else None

    with open("data.txt", "r", encoding='utf-8') as file:
        content = file.read().strip()

    if username and is_original_post(event) and content == "/start":
        num = ALL_ID.index(username)
        if event.message.message:
            await edit_text_message(event, num)
        elif event.message.media:
            await edit_caption_message(event, num)


if __name__ == "__main__":
    print("Bot ishga tushdi...")
    client.start()
    client.run_until_disconnected()