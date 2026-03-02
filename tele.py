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
from pathlib import Path

from logging_setup import setup_logging

setup_logging()
logger = logging.getLogger("posteditor.tele")
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.txt"

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
    chat_username = getattr(getattr(event, "chat", None), "username", None)
    is_allowed = bool(chat_username and chat_username in ALL_ID)
    is_forwarded = bool(event.fwd_from)
    if not is_allowed or is_forwarded:
        logger.info(
            "Event skip (original emas): chat_username=%s, allowed=%s, forwarded=%s, message_id=%s",
            chat_username,
            is_allowed,
            is_forwarded,
            getattr(getattr(event, "message", None), "id", None),
        )
    return is_allowed and not is_forwarded

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
    logger.info(
        "NewMessage event: chat_id=%s, username=%s, message_id=%s, grouped_id=%s",
        event.chat_id,
        getattr(getattr(event, "chat", None), "username", None),
        event.message.id,
        event.message.grouped_id,
    )

    if not is_original_post(event):
        return

    try:
        with open(DATA_FILE, "r", encoding='utf-8') as file:
            content = file.read().strip()
    except FileNotFoundError:
        logger.warning("data.txt topilmadi: %s", DATA_FILE)
        return

    logger.info("State content: '%s'", content)
    if content != "/start":
        logger.info("Event skip (state /start emas): message_id=%s", event.message.id)
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
    try:
        num = ALL_ID.index(username)
    except ValueError:
        logger.warning("ALL_ID ichidan topilmadi (album): username=%s", username)
        return

    if main_event.message.message:
        await edit_text_message(main_event, num)
    else:
        await edit_caption_message(main_event, num)

# Yakka xabarni qayta ishlash
async def process_single_message(event):
    username = event.chat.username
    try:
        num = ALL_ID.index(username)
    except ValueError:
        logger.warning("ALL_ID ichidan topilmadi (single): username=%s", username)
        return

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
    if conn is None or cur is None:
        logger.error("DB ulanmagan: send_basa bajarilmadi. group_id=%s, msg_ids=%s", group_id, msg_ids)
        return

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
            log_info(f"Bot ishga tushdi... session={SESSION_NAME}, data_file={DATA_FILE}")
            await client.start()
            me = await client.get_me()
            logger.info("Telethon authorized: id=%s username=%s", me.id, me.username)
            await client.run_until_disconnected()
        except Exception as e:
            log_error(f"Bot o'chdi. Xato: {str(e)}. 5 soniyadan keyin qayta ishga tushiriladi.")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
