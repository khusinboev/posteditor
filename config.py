from telethon.tl.types import (
    MessageEntityMention,
    MessageEntityBold,
    MessageEntityTextUrl,
    MessageEntityCustomEmoji
)
import os
import logging
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _to_int_list(raw_value: str, default: list[int]) -> list[int]:
    if not raw_value:
        return default
    values = []
    for item in raw_value.split(","):
        item = item.strip()
        if item:
            values.append(int(item))
    return values


def _to_str_list(raw_value: str, default: list[str]) -> list[str]:
    if not raw_value:
        return default
    return [item.strip() for item in raw_value.split(",") if item.strip()]


logger = logging.getLogger("posteditor")

def log_error(message):
    logger.error(message)

def log_info(message):
    logger.info(message)

# API sozlamalari
API_ID = int(os.getenv("API_ID", "12345678"))
API_HASH = os.getenv("API_HASH", "abcdef1234567890abcdef1234567890")
SESSION_NAME = str((BASE_DIR / os.getenv("SESSION_NAME", "my_bot")).resolve())
BOT_TOKEN = os.getenv("BOT_TOKEN", "BOT_TOKEN")

# Adminlar
admin = _to_int_list(os.getenv("ADMIN_IDS", ""), [619839487, 1918760732])

# Telegram kanal identifikatorlari
ALL_ID = _to_str_list(
    os.getenv("ALL_ID", ""),
    ["nodavlattalim", "abitur24", "Talim_Live", "Talim24uz", "ai_lingoBot", "nodavlattalim_uz", "Axmadjanovuz"]
)


# Kanalga qo'shilgan matnlar
ALL_TEXT = [
    "🇺🇿 @nodavlattalim — nodavlat oliy ta’lim muassasalari haqida rasmiy xabarlar!",
    "Safimizga qo'shiling👇\nhttps://t.me/+Xa6LRjERxwo4Njdi\nhttps://t.me/+Xa6LRjERxwo4Njdi",
    "Ta‘lim tizimiga oid yangiliklar:\n➡️ @Talim_Live",
    "✅️@Talim24uz",
    "✅️@Talim24uz",
    "👉 nodavlattalim.uz – rasmiy kanali", 
    "👉 @Axmadjanovuz"
]

# Har bir maxsus emoji uchun offset va id
CUSTOM_EMOJI_MAP = {
    0: (4, 5325506731164312731),  # 🇺🇿
    3: (2, 5350384878254826109),  # ✅
    4: (2, 5350384878254826109),  # ✅
}
RAW_ENTITIES = {
    0: [  # 🇺🇿 @nodavlattalim
        {"offset": 0, "length": 4, "type": "custom_emoji", "custom_emoji_id": "5325506731164312731"},
        {"offset": 5, "length": 14, "type": "mention"},
        {"offset": 5, "length": 14, "type": "bold"},
        {"offset": 19, "length": 60, "type": "bold"},
    ],
    1: [  # Safimizga qo'shiling👇
        {"offset": 0, "length": 22, "type": "bold"}
    ],
    2: [  # Ta‘lim tizimiga oid yangiliklar:
        {"offset": 0, "length": 33, "type": "bold"},
        {"offset": 37, "length": 11, "type": "mention"}
    ],
    3: [  # ✅️@Talim24uz
        {"offset": 0, "length": 2, "type": "custom_emoji", "custom_emoji_id": "5350384878254826109"},
        {"offset": 2, "length": 10, "type": "mention"},
    ],
    4: [  # ✅️@Talim24uz (yana qaytgan)
        {"offset": 0, "length": 2, "type": "custom_emoji", "custom_emoji_id": "5350384878254826109"},
        {"offset": 2, "length": 10, "type": "mention"},
    ],
    5: [  # Ta‘lim tizimiga oid yangiliklar:
        {"offset": 0, "length": 35, "type": "bold"},
    {"offset": 3, "length": 16, "type": "text_link", "url": "https://t.me/nodavlattalim_uz"},
        {"offset": 37, "length": 11, "type": "mention"}
    ]
}


def entities_right(original_text: str, num: int):
    final_entities = []

    # 1. CUSTOM_EMOJI_MAP dan custom emoji entity
    if num in CUSTOM_EMOJI_MAP:
        emoji_length, emoji_id = CUSTOM_EMOJI_MAP[num]
        offset = 0 if len(original_text) == 0 else len(original_text.encode('utf-16-le')) // 2 + 2
        final_entities.append(MessageEntityCustomEmoji(
            offset=offset,
            length=emoji_length,
            document_id=emoji_id
        ))

    # 2. Qo‘shimcha entitylar
    if num in RAW_ENTITIES:
        for ent in RAW_ENTITIES[num]:
            t = ent.get("type")
            offset = ent.get("offset") if len(original_text) == 0 else len(original_text.encode('utf-16-le')) // 2 + 2 + ent.get("offset")
            length = ent.get("length")

            if t == "mention":
                final_entities.append(MessageEntityMention(offset=offset, length=length))
            elif t == "bold":
                final_entities.append(MessageEntityBold(offset=offset, length=length))
            elif t == "custom_emoji":
                emoji_id = int(ent.get("custom_emoji_id"))
                final_entities.append(MessageEntityCustomEmoji(
                    offset=offset,
                    length=length,
                    document_id=emoji_id
                ))
            elif t == "text_link":
                url = ent.get("url")
                final_entities.append(MessageEntityTextUrl(offset=offset, length=length, url=url))

    return final_entities
