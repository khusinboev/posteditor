from telethon import TelegramClient, events
from config import (
    API_ID, API_HASH, SESSION_NAME,
    ALL_ID, ALL_TEXT,
    entities_right,
    log_error, log_info, cur, conn
)
from collections import defaultdict
import asyncio
import logging

from logging_setup import setup_logging

setup_logging()
logger = logging.getLogger("posteditor.tele")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Albomli postlar uchun vaqtinchalik saqlovchi struktura
album_buffer = defaultdict(list)
album_timers = {}

# Premium emojilarni olish
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

# Post original ekanligini tekshiradi (forward emas va belgilangan kanal)
def is_original_post(event):
    return (
        event.chat and
        event.chat.username in ALL_ID and
        not event.fwd_from
    )

# Textli postni tahrirlash
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

# Media post captionini tahrirlash
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

# Asosiy postlarni (yangi xabarlarni) tutish
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

# Albomli postni qayta ishlash
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

# Yakka xabarni qayta ishlash
async def process_single_message(event):
    username = event.chat.username
    num = ALL_ID.index(username)

    if event.message.message:
        await edit_text_message(event, num)
    elif event.message.media:
        await edit_caption_message(event, num)


# 🆕 Guruhlardan kelgan comment xabarlarni tutish va tekshirish
@client.on(events.MessageDeleted(chats=["NT_muhokama", "kepquay"]))
async def deleted_comment_handler(event):
    await send_basa(event.chat_id, event.deleted_ids)

# send_basa funksiyadi
async def send_basa(group_id: int, msg_ids: list[int]):
    try:
        # 1. Hammasini olish
        cur.execute("""
            SELECT user_id, message_id, length FROM comment_messages
            WHERE group_id = %s AND message_id = ANY(%s)
        """, (group_id, msg_ids))
        results = cur.fetchall()

        if not results:
            logger.info("Hech narsa topilmadi: group_id=%s, msg_ids=%s", group_id, msg_ids)
            return

        user_stats = defaultdict(lambda: [0, 0])  # {user_id: [count, length]}
        for user_id, message_id, length in results:
            user_stats[user_id][0] += 1
            user_stats[user_id][1] += length

        # 2. comment_messages dan o‘chirish
        cur.execute("""
            DELETE FROM comment_messages
            WHERE group_id = %s AND message_id = ANY(%s)
        """, (group_id, msg_ids))

        # 3. user_comments yangilash
        for user_id, (count, total_length) in user_stats.items():
            cur.execute("""
                UPDATE user_comments
                SET count = count - %s,
                    lengths = lengths - %s
                WHERE group_id = %s AND user_id = %s
            """, (count, total_length, group_id, user_id))

        conn.commit()
        logger.info("Batch o‘chirildi: %s ta xabar", len(results))

    except Exception as e:
        conn.rollback()
        logger.exception("send_basa_batch xatolik: %s", e)


# Botni ishga tushuruvchi funksiya
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
