from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, MessageNotModifiedError, ChatWriteForbiddenError
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
from typing import Optional

from logging_setup import setup_logging

setup_logging()
logger = logging.getLogger("posteditor.tele")
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.txt"

client = TelegramClient(
    SESSION_NAME,
    API_ID,
    API_HASH,
    # Katta kanallarda ulanish sifatini oshirish uchun
    connection_retries=10,
    retry_delay=3,
    timeout=30,
)

# Albomli postlar uchun vaqtinchalik saqlovchi struktura
album_buffer = defaultdict(list)
album_timers = {}

# chat_id -> entity cache (username resolve qilishni kamaytirish uchun)
_entity_cache: dict = {}


def _normalize_channel_username(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value.strip().lstrip("@").lower()


# kanalni topish uchun keshlar
_channel_index_by_username: dict[str, int] = {}
for i, raw_username in enumerate(ALL_ID):
    normalized_username = _normalize_channel_username(raw_username)
    if normalized_username:
        _channel_index_by_username[normalized_username] = i

_channel_index_by_id: dict[int, int] = {}


# ─────────────────────────────────────────────
# Yordamchi: entity cache (katta kanallarda tez ishlash)
# ─────────────────────────────────────────────
async def get_entity_cached(chat_id: int):
    """
    chat_id orqali entity oladi va keshda saqlaydi.
    Har safar username resolve qilmaydi — katta kanallarda
    bu kechikishning asosiy sababi edi.
    """
    if chat_id not in _entity_cache:
        try:
            entity = await client.get_entity(chat_id)
            _entity_cache[chat_id] = entity
            logger.info("Entity keshlandi: chat_id=%s", chat_id)
        except Exception as e:
            logger.warning("Entity olinmadi (chat_id=%s): %s", chat_id, e)
            return chat_id  # fallback: to'g'ridan-to'g'ri chat_id ishlatamiz
    return _entity_cache[chat_id]


# ─────────────────────────────────────────────
# Premium emojilarni olish
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# Post original ekanligini tekshiradi
# ─────────────────────────────────────────────
def is_original_post(event, channel_index: Optional[int]):
    """
    FIX: Avval chat_username None bo'lsa warn chiqarib False qaytaradi.
    Katta kanallarda chat entity ba'zan yuklanmagan bo'ladi.
    """
    chat = getattr(event, "chat", None)
    chat_username = getattr(chat, "username", None)

    is_allowed = channel_index is not None
    is_forwarded = bool(event.fwd_from)

    if not is_allowed or is_forwarded:
        logger.info(
            "Event skip: chat_id=%s, chat_username=%s, allowed=%s, forwarded=%s, message_id=%s",
            getattr(event, "chat_id", None),
            chat_username,
            is_allowed,
            is_forwarded,
            getattr(getattr(event, "message", None), "id", None),
        )
    return is_allowed and not is_forwarded


async def resolve_channel_index(event) -> Optional[int]:
    chat_id = getattr(event, "chat_id", None)
    if chat_id in _channel_index_by_id:
        return _channel_index_by_id[chat_id]

    chat = getattr(event, "chat", None)
    normalized_username = _normalize_channel_username(getattr(chat, "username", None))
    if normalized_username in _channel_index_by_username:
        index = _channel_index_by_username[normalized_username]
        if chat_id is not None:
            _channel_index_by_id[chat_id] = index
        return index

    if chat_id is not None:
        try:
            entity = await get_entity_cached(chat_id)
            normalized_entity_username = _normalize_channel_username(getattr(entity, "username", None))
            if normalized_entity_username in _channel_index_by_username:
                index = _channel_index_by_username[normalized_entity_username]
                _channel_index_by_id[chat_id] = index
                return index
        except Exception as e:
            logger.warning("resolve_channel_index xatolik: chat_id=%s, xato=%s", chat_id, e)

    return None


# ─────────────────────────────────────────────
# Textli postni tahrirlash
# ─────────────────────────────────────────────
async def edit_text_message(event, num: int, retry: int = 0):
    """
    FIX 1: entity=chat_id (raqamli) — username resolve qilmaydi, tez ishlaydi.
    FIX 2: FloodWaitError ushlaydi va kutib qayta urinadi.
    FIX 3: MessageNotModifiedError — xatosiz o'tkazib yuboradi.
    FIX 4: ChatWriteForbiddenError — ruxsat yo'qligini aniq log qiladi.
    """
    try:
        original_text = event.message.message or ""
        add_text = ALL_TEXT[num]

        if add_text.strip() in original_text:
            log_info(f"Allaqachon mavjud (text): {event.message.id}")
            return

        new_text = f"{original_text}\n\n{add_text}"
        entities = get_premium_emojis(event.message)
        entities += entities_right(original_text, num)

        # FIX: username o'rniga chat_id — katta kanallarda ancha tez
        entity = await get_entity_cached(event.chat_id)

        await client.edit_message(
            entity=entity,
            message=event.message.id,
            text=new_text,
            link_preview=False,
            formatting_entities=entities,
        )
        log_info(f"Tahrirlandi (text): {event.message.id}")

    except FloodWaitError as e:
        # Telegram bizni chekladi — kutib qayta urinish
        wait = e.seconds + 2
        logger.warning(
            "FloodWait (text): %s soniya kutilmoqda... message_id=%s",
            wait, event.message.id
        )
        await asyncio.sleep(wait)
        if retry < 3:
            await edit_text_message(event, num, retry=retry + 1)
        else:
            log_error(f"FloodWait: 3 urinishdan keyin ham muvaffaqiyatsiz (text): {event.message.id}")

    except MessageNotModifiedError:
        # Matn o'zgartirilmagan — xato emas, shunchaki o'tkazib yuboramiz
        log_info(f"Matn o'zgartirilmagan (text): {event.message.id}")

    except ChatWriteForbiddenError:
        log_error(f"Kanalga yozish taqiqlangan (text): chat_id={event.chat_id}")

    except Exception as e:
        log_error(f"Xatolik (text): {type(e).__name__}: {e} | message_id={event.message.id}")


# ─────────────────────────────────────────────
# Media post captionini tahrirlash
# ─────────────────────────────────────────────
async def edit_caption_message(event, num: int, retry: int = 0):
    """
    FIX 1: entity=chat_id (raqamli) — tez ishlaydi.
    FIX 2: FloodWaitError ushlaydi va kutib qayta urinadi.
    FIX 3: MessageNotModifiedError — xatosiz o'tkazib yuboradi.
    FIX 4: ChatWriteForbiddenError — ruxsat yo'qligini aniq log qiladi.
    """
    try:
        caption = event.message.message or ""
        add_text = ALL_TEXT[num]

        if add_text.strip() in caption:
            log_info(f"Allaqachon mavjud (caption): {event.message.id}")
            return

        new_caption = f"{caption}\n\n{add_text}" if caption else add_text
        entities = get_premium_emojis(event.message)
        entities += entities_right(caption, num)

        # FIX: username o'rniga chat_id
        entity = await get_entity_cached(event.chat_id)

        await client.edit_message(
            entity=entity,
            message=event.message.id,
            text=new_caption,
            link_preview=False,
            formatting_entities=entities,
        )
        log_info(f"Tahrirlandi (caption): {event.message.id}")

    except FloodWaitError as e:
        wait = e.seconds + 2
        logger.warning(
            "FloodWait (caption): %s soniya kutilmoqda... message_id=%s",
            wait, event.message.id
        )
        await asyncio.sleep(wait)
        if retry < 3:
            await edit_caption_message(event, num, retry=retry + 1)
        else:
            log_error(f"FloodWait: 3 urinishdan keyin ham muvaffaqiyatsiz (caption): {event.message.id}")

    except MessageNotModifiedError:
        log_info(f"Matn o'zgartirilmagan (caption): {event.message.id}")

    except ChatWriteForbiddenError:
        log_error(f"Kanalga yozish taqiqlangan (caption): chat_id={event.chat_id}")

    except Exception as e:
        log_error(f"Xatolik (caption): {type(e).__name__}: {e} | message_id={event.message.id}")


# ─────────────────────────────────────────────
# Asosiy handler — yangi postlarni tutadi
# ─────────────────────────────────────────────
@client.on(events.NewMessage())
async def handler(event):
    channel_index = await resolve_channel_index(event)

    logger.info(
        "NewMessage event: chat_id=%s, username=%s, index=%s, message_id=%s, grouped_id=%s",
        event.chat_id,
        getattr(getattr(event, "chat", None), "username", None),
        channel_index,
        event.message.id,
        event.message.grouped_id,
    )

    if not is_original_post(event, channel_index):
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
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
        album_buffer[grouped_id].append((event, channel_index))
        # FIX: ensure_future — handler bloklanmaydi, event loop to'silmaydi
        # Avvalgi kodda `await asyncio.sleep(1.5)` handler ichida edi —
        # bu katta kanallarda keyingi eventlarni kechiktirardi.
        if grouped_id not in album_timers:
            album_timers[grouped_id] = True
            asyncio.ensure_future(handle_album_with_delay(grouped_id))
    else:
        # Yakka xabarni ham ensure_future bilan — handler zudlik bilan qaytadi
        asyncio.ensure_future(process_single_message(event, channel_index))


# ─────────────────────────────────────────────
# Album: kechikish bilan qayta ishlash
# ─────────────────────────────────────────────
async def handle_album_with_delay(grouped_id):
    """
    FIX: handler dan ajratildi. ensure_future orqali chaqiriladi.
    Endi handler bloklanmaydi — katta kanallarda ham tez ishlaydi.
    """
    await asyncio.sleep(1.5)
    await process_album(grouped_id)
    album_timers.pop(grouped_id, None)


# ─────────────────────────────────────────────
# Albomli postni qayta ishlash
# ─────────────────────────────────────────────
async def process_album(grouped_id):
    evts = album_buffer.pop(grouped_id, [])
    if not evts:
        return

    main_event, channel_index = evts[0]
    if channel_index is None:
        logger.warning("process_album: kanal aniqlanmadi, chat_id=%s", main_event.chat_id)
        return

    if main_event.message.message:
        await edit_text_message(main_event, channel_index)
    else:
        await edit_caption_message(main_event, channel_index)


# ─────────────────────────────────────────────
# Yakka xabarni qayta ishlash
# ─────────────────────────────────────────────
async def process_single_message(event, channel_index: Optional[int]):
    if channel_index is None:
        logger.warning("process_single_message: kanal aniqlanmadi, chat_id=%s", event.chat_id)
        return

    if event.message.message:
        await edit_text_message(event, channel_index)
    elif event.message.media:
        await edit_caption_message(event, channel_index)


# ─────────────────────────────────────────────
# O'chirilgan comment xabarlarni tutish
# ─────────────────────────────────────────────
@client.on(events.MessageDeleted(chats=["NT_muhokama", "kepquay"]))
async def deleted_comment_handler(event):
    await send_basa(event.chat_id, event.deleted_ids)


# ─────────────────────────────────────────────
# send_basa — DB ga o'chirilgan xabarlarni yozish
# ─────────────────────────────────────────────
async def send_basa(group_id: int, msg_ids: list[int]):
    if conn is None or cur is None:
        logger.error(
            "DB ulanmagan: send_basa bajarilmadi. group_id=%s, msg_ids=%s",
            group_id, msg_ids
        )
        return

    try:
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

        cur.execute("""
            DELETE FROM comment_messages
            WHERE group_id = %s AND message_id = ANY(%s)
        """, (group_id, msg_ids))

        for user_id, (count, total_length) in user_stats.items():
            cur.execute("""
                UPDATE user_comments
                SET count = count - %s,
                    lengths = lengths - %s
                WHERE group_id = %s AND user_id = %s
            """, (count, total_length, group_id, user_id))

        conn.commit()
        logger.info("Batch o'chirildi: %s ta xabar", len(results))

    except Exception as e:
        conn.rollback()
        logger.exception("send_basa_batch xatolik: %s", e)


# ─────────────────────────────────────────────
# Botni ishga tushuruvchi funksiya
# ─────────────────────────────────────────────
async def main():
    while True:
        try:
            log_info(f"Bot ishga tushdi... session={SESSION_NAME}, data_file={DATA_FILE}")
            await client.start()
            me = await client.get_me()
            logger.info("Telethon authorized: id=%s username=%s", me.id, me.username)

            # Barcha kanallar uchun entity oldindan keshlash
            # Katta kanallarda birinchi post tezroq tahrirlanadi
            logger.info("Kanallar entity keshlanmoqda...")
            for index, channel_username in enumerate(ALL_ID):
                try:
                    entity = await client.get_entity(channel_username)
                    _entity_cache[entity.id] = entity

                    normalized_username = _normalize_channel_username(channel_username)
                    if normalized_username:
                        _channel_index_by_username[normalized_username] = index

                    entity_username = _normalize_channel_username(getattr(entity, "username", None))
                    if entity_username:
                        _channel_index_by_username[entity_username] = index

                    _channel_index_by_id[entity.id] = index
                    logger.info("Keshlandi: @%s -> id=%s, index=%s", channel_username, entity.id, index)
                except Exception as e:
                    logger.warning("Entity olinmadi (@%s): %s", channel_username, e)

            logger.info("Entity keshlash tugadi. Bot ishlamoqda...")
            await client.run_until_disconnected()

        except Exception as e:
            log_error(f"Bot o'chdi. Xato: {type(e).__name__}: {str(e)}. 5 soniyadan keyin qayta ishga tushiriladi.")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())