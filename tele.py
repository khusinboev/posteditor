from telethon import TelegramClient, events
from config import API_ID, API_HASH, SESSION_NAME, ALL_ID, ALL_TEXT, entities_right
from telethon.tl.types import MessageEntityCustomEmoji
import emoji

# TelegramClient yaratamiz
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


def get_premium_emojis(message):
    """Xabar yoki caption uchun emoji'larni olish"""
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
    """Xabar original post ekanligini tekshiradi (forward emas)"""
    return (
        event.chat and
        event.chat.username in ALL_ID and
        not event.fwd_from
    )


async def edit_text_message(event, num: int):
    """Textli xabarni tahrirlash"""
    try:
        original_text = event.message.message
        new_text = f"{original_text}\n\n{ALL_TEXT[num]}"
        
        # Xabarning yangi versiyasini tahrirlaymiz, emoji qo‘shish
        await client.edit_message(
            entity=ALL_ID[num],
            message=event.message.id,
            text=new_text,
            link_preview=False,
            formatting_entities=get_premium_emojis(event.message) + entities_right(original_text, num)
        )
        print(f"Tahrirlandi: {event.message.id}")
    except Exception as e:
        print(f"Xatolik text tahririda: {e}")


async def edit_caption_message(event, num: int):
    """Captionli xabarni tahrirlash"""
    try:
        caption = event.message.message or ""
        new_caption = f"{caption}\n\n{ALL_TEXT[num]}" if caption else ALL_TEXT[num]
        
        # Captionni tahrirlaymiz, emoji qo‘shish
        await client.edit_message(
            entity=ALL_ID[num],
            message=event.message.id,
            text=new_caption,
            link_preview=False,
            formatting_entities=get_premium_emojis(event.message) + entities_right(caption, num)
        )
        print(f"Caption tahrirlandi: {event.message.id}")
    except Exception as e:
        print(f"Xatolik caption tahririda: {e}")


@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    """Yangi xabarni qabul qilish va uni tahrirlash"""
    print("Yangi xabar qabul qilindi")
    username = event.chat.username if event.chat else None
    print("Foydalanuvchi:", username)

    with open("data.txt", "r", encoding='utf-8') as file:
        content = file.read().strip()

    if username and is_original_post(event) and content == "/start":
        num = ALL_ID.index(username)
        if event.message.message:  # matnli
            await edit_text_message(event, num)
        elif event.message.media:  # media bilan
            await edit_caption_message(event, num)


if __name__ == "__main__":
    print("Bot ishga tushdi...")
    client.start()
    client.run_until_disconnected()