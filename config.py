from telethon.tl.types import (
    MessageEntityMention,
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityTextUrl,
    MessageEntityCustomEmoji,
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


def log_error(message: str) -> None:
    logger.error(message)


def log_info(message: str) -> None:
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
    ["nodavlattalim", "abitur24", "Talim_Live", "Talim24uz", "Axmadjanovuz", "nodavlattalim_uz", "ai_lingoBot"],
)


# ---------------------------------------------------------------------------
# Kanalga qo'shiladigan matnlar
# ---------------------------------------------------------------------------
# Index  Kanal(lar)
# ─────  ──────────────────────────────────────────────────────────────────
#   0    nodavlattalim
#   1    nodavlattalim, abitur24, Talim_Live, Talim24uz, ai_lingoBot  (Safimizga)
#   2    Talim_Live
#   3    Talim24uz
#   4    (avval Talim24uz uchun edi — hozir index 3 bilan bir xil edi, saqlab qolindi)
#   5    nodavlattalim_uz
#   6    Axmadjanovuz
#   7    abitur24, Talim_Live, Talim24uz, ai_lingoBot  ← YANGI (premium emoji)
# ---------------------------------------------------------------------------
ALL_TEXT = [
    # 0 — nodavlattalim
    "🇺🇿 @nodavlattalim — nodavlat oliy ta'lim muassasalari haqida rasmiy xabarlar!",

    # 1 — "Safimizga qo'shiling" (bir nechta kanalga)
    "Safimizga qo'shiling👇\nhttps://t.me/+Xa6LRjERxwo4Njdi\nhttps://t.me/+Xa6LRjERxwo4Njdi",

    # 2 — Talim_Live
    "Ta'lim tizimiga oid yangiliklar:\n➡️ @Talim_Live",

    # 3 — Talim24uz
    "✅️@Talim24uz",

    # 4 — (zaxira / eski entry, saqlab qolindi)
    "✅️@Talim24uz",

    # 5 — nodavlattalim_uz (text_link bilan)
    "👉 nodavlattalim.uz – rasmiy kanali",

    # 6 — Axmadjanovuz
    "👉 @Axmadjanovuz",

    # 7 — abitur24 | Talim_Live | Talim24uz | ai_lingoBot
    # \n\n bilan boshlanadi — original xabarga qo'shilganda bo'sh qator ajratadi.
    # Entity offset'lari: JSON offset + 2  (chunki \n\n = 2 UTF-16 unit)
    "\n\n✔️ @mandatjavobbot orqali istalgan ta'lim yo'nalishlarining "
    "2025-2026-o'quv yilidagi o'tish ballari bilan tanishishingiz mumkin."
    "\n\n🖊 @BMB_testbot orqali maxsus diagnostik testlarni ishlab, "
    "o'z bilimingizni bepulga sinovdan o'tkazishingiz mumkin.",
]


# ---------------------------------------------------------------------------
# RAW_ENTITIES
# Barcha entity'lar shu yerda — CUSTOM_EMOJI_MAP alohida saqlanmaydi
# (duplicate bo'lishini oldini olish uchun).
# offset'lar: matn BOSHIDAN hisoblangan UTF-16-LE unit'lar.
# entities_right() chaqirilganda original_text uzunligi avtomatik qo'shiladi.
# ---------------------------------------------------------------------------
RAW_ENTITIES: dict[int, list[dict]] = {
    # 0 — 🇺🇿 @nodavlattalim
    0: [
        {"offset": 0,  "length": 4,  "type": "custom_emoji", "custom_emoji_id": "5325506731164312731"},  # 🇺🇿
        {"offset": 5,  "length": 14, "type": "mention"},   # @nodavlattalim
        {"offset": 5,  "length": 14, "type": "bold"},
        {"offset": 19, "length": 60, "type": "bold"},
    ],

    # 1 — Safimizga qo'shiling👇
    1: [
        {"offset": 0, "length": 22, "type": "bold"},
    ],

    # 2 — Ta'lim tizimiga oid yangiliklar: ➡️ @Talim_Live
    2: [
        {"offset": 0,  "length": 33, "type": "bold"},
        {"offset": 37, "length": 11, "type": "mention"},   # @Talim_Live
    ],

    # 3 — ✅️@Talim24uz
    3: [
        {"offset": 0, "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5350384878254826109"},  # ✅
        {"offset": 2, "length": 10, "type": "mention"},    # @Talim24uz
    ],

    # 4 — ✅️@Talim24uz (zaxira)
    4: [
        {"offset": 0, "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5350384878254826109"},
        {"offset": 2, "length": 10, "type": "mention"},
    ],

    # 5 — 👉 nodavlattalim.uz (text_link)
    5: [
        {"offset": 0,  "length": 35, "type": "bold"},
        {"offset": 3,  "length": 16, "type": "text_link", "url": "https://t.me/nodavlattalim_uz"},
        {"offset": 37, "length": 11, "type": "mention"},
    ],

    # 6 — 👉 @Axmadjanovuz
    6: [
        {"offset": 3, "length": 14, "type": "mention"},
    ],

    # 7 — ✔️ @mandatjavobbot … 🖊 @BMB_testbot …
    # Offset'lar JSON'dagi qiymat + 2 (\n\n prefix = 2 UTF-16 unit)
    # Barcha offset'lar python skript bilan tekshirilgan (bexato ✓)
    7: [
        # ✔️  (U+2714 + U+FE0F, har biri 1 UTF-16 unit → length=2)
        {"offset": 2,   "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5321210956414459578"},
        # @mandatjavobbot
        {"offset": 5,   "length": 15, "type": "mention"},
        {"offset": 5,   "length": 15, "type": "bold"},
        {"offset": 5,   "length": 15, "type": "italic"},
        # " orqali istalgan ta'lim yo'nalishlarining "
        {"offset": 20,  "length": 42, "type": "italic"},
        # "2025-2026-o'quv yilidagi o'tish ballari"
        {"offset": 62,  "length": 39, "type": "bold"},
        {"offset": 62,  "length": 39, "type": "italic"},
        # "bilan tanishishingiz mumkin."
        {"offset": 102, "length": 28, "type": "italic"},
        # 🖊  (U+1F58A, surrogate pair → length=2)
        {"offset": 132, "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5321223519193800525"},
        # space after 🖊
        {"offset": 134, "length": 1,  "type": "italic"},
        # @BMB_testbot
        {"offset": 135, "length": 12, "type": "mention"},
        {"offset": 135, "length": 12, "type": "bold"},
        {"offset": 135, "length": 12, "type": "italic"},
        # " orqali maxsus "
        {"offset": 147, "length": 15, "type": "italic"},
        # "diagnostik testlarni ishlab, o'z bilimingizni bepulga sinovdan o'tkazishingiz mumkin."
        {"offset": 162, "length": 84, "type": "italic"},
        {"offset": 162, "length": 77, "type": "bold"},
    ],
}


# ---------------------------------------------------------------------------
# Entity builder
# ---------------------------------------------------------------------------
def entities_right(original_text: str, num: int) -> list:
    """
    original_text — shu paytgacha yig'ilgan xabar matni (qo'shimcha qo'shilishidan oldin).
    num           — ALL_TEXT / RAW_ENTITIES indeksi.

    Qaytaradi: Telethon MessageEntity ob'ektlari ro'yxati.

    Offset hisoblash:
        original_text bo'sh bo'lsa  → offset = entry_offset
        bo'sh bo'lmasa              → offset = utf16(original_text) + 2 + entry_offset
        (+2 = ikki qo'shni belgi: odatda '\n\n' yoki separator)
    """
    if num not in RAW_ENTITIES:
        return []

    final_entities: list = []
    base_offset = (
        0
        if not original_text
        else len(original_text.encode("utf-16-le")) // 2 + 2
    )

    for ent in RAW_ENTITIES[num]:
        t = ent["type"]
        offset = base_offset + ent["offset"]
        length = ent["length"]

        match t:
            case "mention":
                final_entities.append(MessageEntityMention(offset=offset, length=length))
            case "bold":
                final_entities.append(MessageEntityBold(offset=offset, length=length))
            case "italic":
                final_entities.append(MessageEntityItalic(offset=offset, length=length))
            case "text_link":
                final_entities.append(
                    MessageEntityTextUrl(offset=offset, length=length, url=ent["url"])
                )
            case "custom_emoji":
                final_entities.append(
                    MessageEntityCustomEmoji(
                        offset=offset,
                        length=length,
                        document_id=int(ent["custom_emoji_id"]),
                    )
                )
            case _:
                log_error(f"entities_right: noma'lum entity type '{t}' (num={num})")

    return final_entities