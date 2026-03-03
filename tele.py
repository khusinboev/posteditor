import asyncio
import logging
from pathlib import Path
from typing import Any, Optional

from telethon import TelegramClient
from telethon.errors import ChatWriteForbiddenError, FloodWaitError, MessageNotModifiedError
from telethon.tl.functions.account import UpdateStatusRequest

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
POLL_INTERVAL_SECONDS = 10
FETCH_LIMIT_PER_CHANNEL = 15

client = TelegramClient(
    SESSION_NAME,
    API_ID,
    API_HASH,
    connection_retries=10,
    retry_delay=3,
    timeout=30,
)

channels: list[dict[str, Any]] = []


def _read_state() -> str:
    try:
        return DATA_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        logger.warning("State file topilmadi: %s", DATA_FILE)
        return ""


def _is_forwarded(message) -> bool:
    return bool(getattr(message, "fwd_from", None) or getattr(message, "forward", None))


def _existing_entities(message) -> list:
    entities = getattr(message, "entities", None)
    if entities:
        return list(entities)
    return []


async def _edit_message_with_retry(entity, message, channel_index: int, retry: int = 0) -> bool:
    original_text = message.message or ""
    suffix = ALL_TEXT[channel_index]

    if suffix.strip() in original_text:
        log_info(f"Allaqachon qo'shilgan: chat_id={getattr(entity, 'id', None)}, message_id={message.id}")
        return True

    if _is_forwarded(message):
        logger.info("Skip forwarded post: chat_id=%s, message_id=%s", getattr(entity, "id", None), message.id)
        return True

    new_text = f"{original_text}\n\n{suffix}" if original_text else suffix
    formatting_entities = _existing_entities(message) + entities_right(original_text, channel_index)

    try:
        await client.edit_message(
            entity=entity,
            message=message.id,
            text=new_text,
            link_preview=False,
            formatting_entities=formatting_entities,
        )
        log_info(f"Post tahrirlandi: chat_id={getattr(entity, 'id', None)}, message_id={message.id}")
        return True

    except MessageNotModifiedError:
        log_info(f"MessageNotModified: chat_id={getattr(entity, 'id', None)}, message_id={message.id}")
        return True

    except ChatWriteForbiddenError:
        log_error(f"Ruxsat yo'q (ChatWriteForbidden): chat_id={getattr(entity, 'id', None)}")
        return True

    except FloodWaitError as error:
        wait_seconds = error.seconds + 2
        logger.warning(
            "FloodWait: %s soniya kutamiz (chat_id=%s, message_id=%s, retry=%s)",
            wait_seconds,
            getattr(entity, "id", None),
            message.id,
            retry,
        )
        if retry >= 3:
            log_error(f"FloodWait limit: chat_id={getattr(entity, 'id', None)}, message_id={message.id}")
            return False

        await asyncio.sleep(wait_seconds)
        return await _edit_message_with_retry(entity, message, channel_index, retry=retry + 1)

    except Exception as error:
        logger.exception(
            "Post tahrirlashda xatolik: chat_id=%s, message_id=%s, xato=%s",
            getattr(entity, "id", None),
            message.id,
            error,
        )
        return False


def _pick_album_targets(messages: list[Any]) -> list[Any]:
    grouped: dict[int, list[Any]] = {}
    singles: list[Any] = []

    for msg in messages:
        grouped_id = getattr(msg, "grouped_id", None)
        if grouped_id:
            grouped.setdefault(grouped_id, []).append(msg)
        else:
            singles.append(msg)

    targets = list(singles)

    for _, group_messages in grouped.items():
        target = None
        for msg in group_messages:
            if (msg.message or "").strip():
                target = msg
                break
        if target is None:
            target = sorted(group_messages, key=lambda m: m.id)[0]
        targets.append(target)

    return sorted(targets, key=lambda m: m.id)


async def _poll_single_channel(channel_state: dict[str, Any]) -> None:
    entity = channel_state["entity"]
    index = channel_state["index"]
    title = channel_state["title"]
    last_seen_id = channel_state["last_seen_id"]

    try:
        recent_messages = await client.get_messages(entity, limit=FETCH_LIMIT_PER_CHANNEL)
    except FloodWaitError as error:
        wait_seconds = error.seconds + 2
        logger.warning("FloodWait polling: channel=%s, %s soniya kutamiz", title, wait_seconds)
        await asyncio.sleep(wait_seconds)
        return
    except Exception as error:
        logger.warning("Kanalni o'qishda xatolik: channel=%s, xato=%s", title, error)
        return

    if not recent_messages:
        return

    ordered = sorted(recent_messages, key=lambda msg: msg.id)
    newest_id = ordered[-1].id

    if newest_id <= last_seen_id:
        return

    new_messages = [msg for msg in ordered if msg.id > last_seen_id]
    targets = _pick_album_targets(new_messages)

    logger.info(
        "Yangi postlar topildi: channel=%s, count=%s, from_id=%s, to_id=%s",
        title,
        len(new_messages),
        new_messages[0].id,
        new_messages[-1].id,
    )

    for message in targets:
        if not ((message.message or "").strip() or message.media):
            logger.info("Skip service/empty message: channel=%s, message_id=%s", title, message.id)
            continue
        await _edit_message_with_retry(entity, message, index)

    channel_state["last_seen_id"] = newest_id


async def _poll_loop() -> None:
    while True:
        state = _read_state()
        if state != "/start":
            logger.info("Polling pauza: data.txt='%s' (keraklisi: /start)", state)
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            continue

        for channel_state in channels:
            await _poll_single_channel(channel_state)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)


async def _keep_online_status() -> None:
    while True:
        try:
            await client(UpdateStatusRequest(offline=False))
            logger.info("Online keepalive yuborildi")
        except Exception as error:
            logger.warning("Online keepalive xatolik: %s", error)
        await asyncio.sleep(240)


async def _prepare_channels() -> None:
    channels.clear()

    if len(ALL_ID) != len(ALL_TEXT):
        logger.warning(
            "ALL_ID va ALL_TEXT soni teng emas: channels=%s, texts=%s. Minimum uzunlik ishlatiladi.",
            len(ALL_ID),
            len(ALL_TEXT),
        )

    usable_count = min(len(ALL_ID), len(ALL_TEXT))
    logger.info("Monitoring kanallar soni: %s", usable_count)

    for index in range(usable_count):
        channel_ref = ALL_ID[index]
        try:
            entity = await client.get_entity(channel_ref)
            latest = await client.get_messages(entity, limit=1)
            last_seen_id = latest[0].id if latest else 0

            title = getattr(entity, "title", None) or getattr(entity, "username", None) or str(channel_ref)
            channels.append(
                {
                    "index": index,
                    "entity": entity,
                    "title": title,
                    "last_seen_id": last_seen_id,
                }
            )
            logger.info(
                "Kanal tayyor: index=%s, channel=%s, chat_id=%s, initial_last_seen=%s",
                index,
                title,
                getattr(entity, "id", None),
                last_seen_id,
            )
        except Exception as error:
            logger.warning("Kanalni resolve qilib bo'lmadi (%s): %s", channel_ref, error)


async def main() -> None:
    while True:
        keepalive_task: Optional[asyncio.Task] = None
        polling_task: Optional[asyncio.Task] = None

        try:
            log_info(f"Userbot ishga tushdi. session={SESSION_NAME}")
            await client.start()

            me = await client.get_me()
            logger.info("Authorized: id=%s username=%s", me.id, me.username)

            await client(UpdateStatusRequest(offline=False))
            logger.info("Hisob online holatga o'tkazildi")

            await _prepare_channels()
            keepalive_task = asyncio.create_task(_keep_online_status())
            polling_task = asyncio.create_task(_poll_loop())

            await client.run_until_disconnected()

        except Exception as error:
            log_error(f"Userbot xatolik bilan to'xtadi: {type(error).__name__}: {error}")
            await asyncio.sleep(5)
        finally:
            if keepalive_task and not keepalive_task.done():
                keepalive_task.cancel()
            if polling_task and not polling_task.done():
                polling_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
