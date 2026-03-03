import asyncio
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional

from telethon import TelegramClient, events
from telethon.errors import ChatWriteForbiddenError, FloodWaitError, MessageNotModifiedError

from config import (
    ALL_ID,
    ALL_TEXT,
    API_HASH,
    API_ID,
    SESSION_NAME,
    entities_right,
    log_error,
    log_info,
)
from logging_setup import setup_logging


setup_logging()
logger = logging.getLogger("posteditor.tele")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.txt"

client = TelegramClient(
    SESSION_NAME,
    API_ID,
    API_HASH,
    connection_retries=10,
    retry_delay=3,
    timeout=30,
)

_entity_by_chat_id: dict[int, object] = {}
_channel_index_by_chat_id: dict[int, int] = {}
_channel_index_by_username: dict[str, int] = {}

album_buffer: dict[int, list[tuple[events.NewMessage.Event, int]]] = defaultdict(list)
album_tasks: dict[int, asyncio.Task] = {}


for index, channel in enumerate(ALL_ID):
    username = channel.strip().lstrip("@").lower()
    if username:
        _channel_index_by_username[username] = index


def _state_started() -> bool:
    try:
        return DATA_FILE.read_text(encoding="utf-8").strip() == "/start"
    except FileNotFoundError:
        logger.warning("State file topilmadi: %s", DATA_FILE)
        return False


def _is_forwarded(message) -> bool:
    return bool(getattr(message, "fwd_from", None) or getattr(message, "forward", None))


def _existing_entities(message) -> list:
    entities = getattr(message, "entities", None)
    if entities:
        return list(entities)
    return []


async def _edit_message_with_retry(event: events.NewMessage.Event, channel_index: int, retry: int = 0) -> None:
    message = event.message
    original_text = message.message or ""
    suffix = ALL_TEXT[channel_index]

    if suffix.strip() in original_text:
        log_info(f"Allaqachon qo'shilgan: message_id={message.id}")
        return

    new_text = f"{original_text}\n\n{suffix}" if original_text else suffix
    entities = _existing_entities(message) + entities_right(original_text, channel_index)

    try:
        await client.edit_message(
            entity=event.chat_id,
            message=message.id,
            text=new_text,
            link_preview=False,
            formatting_entities=entities,
        )
        log_info(f"Post tahrirlandi: chat_id={event.chat_id}, message_id={message.id}")

    except MessageNotModifiedError:
        log_info(f"MessageNotModified: message_id={message.id}")

    except ChatWriteForbiddenError:
        log_error(f"Ruxsat yo'q (ChatWriteForbidden): chat_id={event.chat_id}")

    except FloodWaitError as error:
        wait_seconds = error.seconds + 2
        logger.warning(
            "FloodWait: %s soniya kutamiz (message_id=%s, retry=%s)",
            wait_seconds,
            message.id,
            retry,
        )
        if retry >= 3:
            log_error(f"FloodWait limit: message_id={message.id}")
            return
        await asyncio.sleep(wait_seconds)
        await _edit_message_with_retry(event, channel_index, retry=retry + 1)

    except Exception as error:
        logger.exception("Post tahrirlashda xatolik: %s", error)


async def _resolve_channel_index(event: events.NewMessage.Event) -> Optional[int]:
    chat_id = event.chat_id
    if chat_id in _channel_index_by_chat_id:
        return _channel_index_by_chat_id[chat_id]

    chat = getattr(event, "chat", None)
    username = getattr(chat, "username", None)
    if username:
        normalized = username.strip().lstrip("@").lower()
        if normalized in _channel_index_by_username:
            idx = _channel_index_by_username[normalized]
            _channel_index_by_chat_id[chat_id] = idx
            return idx

    return None


def _is_channel_post(event: events.NewMessage.Event) -> bool:
    return bool(event.is_channel and not event.is_group)


async def _process_single(event: events.NewMessage.Event, channel_index: int) -> None:
    if _is_forwarded(event.message):
        return
    await _edit_message_with_retry(event, channel_index)


async def _process_album(grouped_id: int) -> None:
    await asyncio.sleep(1.5)
    entries = album_buffer.pop(grouped_id, [])
    album_tasks.pop(grouped_id, None)

    if not entries:
        return

    first_event, channel_index = entries[0]
    if _is_forwarded(first_event.message):
        return

    target_event = first_event
    for event, _ in entries:
        if (event.message.message or "").strip():
            target_event = event
            break

    await _edit_message_with_retry(target_event, channel_index)


@client.on(events.NewMessage())
async def on_new_message(event: events.NewMessage.Event) -> None:
    if not _state_started():
        return

    if not _is_channel_post(event):
        return

    channel_index = await _resolve_channel_index(event)
    if channel_index is None:
        return

    grouped_id = event.message.grouped_id
    if grouped_id:
        album_buffer[grouped_id].append((event, channel_index))
        if grouped_id not in album_tasks:
            album_tasks[grouped_id] = asyncio.create_task(_process_album(grouped_id))
        return

    asyncio.create_task(_process_single(event, channel_index))


async def _warmup_channel_cache() -> None:
    for index, channel in enumerate(ALL_ID):
        try:
            entity = await client.get_entity(channel)
            _entity_by_chat_id[entity.id] = entity
            _channel_index_by_chat_id[entity.id] = index

            username = getattr(entity, "username", None)
            if username:
                _channel_index_by_username[username.strip().lstrip("@").lower()] = index

            logger.info("Kanal keshlandi: %s -> %s", channel, entity.id)
        except Exception as error:
            logger.warning("Kanalni resolve qilib bo'lmadi (%s): %s", channel, error)


async def main() -> None:
    while True:
        try:
            log_info(f"Userbot ishga tushdi. session={SESSION_NAME}")
            await client.start()
            me = await client.get_me()
            logger.info("Authorized: id=%s username=%s", me.id, me.username)

            await _warmup_channel_cache()
            await client.run_until_disconnected()

        except Exception as error:
            log_error(f"Userbot xatolik bilan to'xtadi: {type(error).__name__}: {error}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
