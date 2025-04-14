from telethon import TelegramClient, events
from config import API_ID, API_HASH, SESSION_NAME, ALL_ID, ALL_TEXT, entities_right, log_error, log_info
from collections import defaultdict
import asyncio
import logging

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

album_buffer = defaultdict(list)
album_timers = {}

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
    return (
        event.chat and
        event.chat.username in ALL_ID and
        not event.fwd_from
    )

async def edit_text_message(event, num: int):
    try:
        original_text = event.message.message or ""
        add_text = ALL_TEXT[num]

        if add_text.strip() in original_text:
            log_info(f"Allaqachon mavjud (text): {event.message.id}")
            return

        new_text = f"{original_text}\n\n{add_text}"
        entities = get_premium_emojis(event.message)
        entities += entities_right(original_text, num)
        await client.edit_message(
            entity=ALL_ID[num],
            message=event.message.id,
            text=new_text,
            link_preview=False,
            formatting_entities=entities,
        )
        log_info(f"Tahrirlandi (text): {event.message.id}")
    except Exception as e:
        log_error(f"Xatolik (text): {e}")

async def edit_caption_message(event, num: int):
    try:
        caption = event.message.message or ""
        add_text = ALL_TEXT[num]

        if add_text.strip() in caption:
            log_info(f"Allaqachon mavjud (caption): {event.message.id}")
            return

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
        log_info(f"Tahrirlandi (caption): {event.message.id}")
    except Exception as e:
        log_error(f"Xatolik (caption): {e}")

@client.on(events.NewMessage(chats=ALL_ID))
async def handler(event):
    if not is_original_post(event):
        return
    with open("data.txt", "r", encoding='utf-8') as file:
        content = file.read().strip()

    if content != "/start":
        return
    grouped_id = event.message.grouped_id

    if grouped_id:
        album_buffer[grouped_id].append(event)
        if grouped_id not in album_timers:
            album_timers[grouped_id] = True
            await asyncio.sleep(1.5)
            await process_album(grouped_id)
            del album_timers[grouped_id]
    else:
        await process_single_message(event)

async def process_album(grouped_id):
    events = album_buffer.pop(grouped_id, [])
    if not events:
        return

    main_event = events[0]
    username = main_event.chat.username
    num = ALL_ID.index(username)
    if main_event.message.message:
        await edit_text_message(main_event, num)
    else:
        await edit_caption_message(main_event, num)

async def process_single_message(event):
    username = event.chat.username
    num = ALL_ID.index(username)
    if event.message.message:
        await edit_text_message(event, num)
    elif event.message.media:
        await edit_caption_message(event, num)

async def main():
    while True:
        try:
            log_info("Bot ishga tushdi...")
            await client.start()
            await client.run_until_disconnected()
        except Exception as e:
            log_error(f"Bot o'chdi. Xato: {str(e)}. 5 soniyadan keyin qayta ishga tushiriladi.")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
