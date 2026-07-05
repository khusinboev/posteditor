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
    return [int(v.strip()) for v in raw_value.split(",") if v.strip()]


def _to_str_list(raw_value: str, default: list[str]) -> list[str]:
    if not raw_value:
        return default
    return [v.strip() for v in raw_value.split(",") if v.strip()]


logger = logging.getLogger("posteditor")


def log_error(message: str) -> None:
    logger.error(message)


def log_info(message: str) -> None:
    logger.info(message)


# ---------------------------------------------------------------------------
# API sozlamalari
# ---------------------------------------------------------------------------
API_ID = int(os.getenv("API_ID", "12345678"))
API_HASH = os.getenv("API_HASH", "abcdef1234567890abcdef1234567890")
SESSION_NAME = str((BASE_DIR / os.getenv("SESSION_NAME", "my_bot")).resolve())
BOT_TOKEN = os.getenv("BOT_TOKEN", "BOT_TOKEN")

admin = _to_int_list(os.getenv("ADMIN_IDS", ""), [619839487, 1918760732])

ALL_ID = _to_str_list(
    os.getenv("ALL_ID", ""),
    ["nodavlattalim", "abitur24", "Talim_Live", "Talim24uz", "Axmadjanovuz", "nodavlattalim_uz", "ai_lingoBot"],
)


# ---------------------------------------------------------------------------
# ALL_TEXT  (indeks = kalit, tele.py tomonidan "\n\n" separator bilan qo'shiladi)
#
# ALL_TEXT[7]: "\n\n" prefix YO'Q — tele.py "\n\n{suffix}" formatida qo'shadi.
# ---------------------------------------------------------------------------
ALL_TEXT: list[str] = [
    # 0 — nodavlattalim
    "🇺🇿 @nodavlattalim — nodavlat oliy ta'lim muassasalari haqida rasmiy xabarlar!",
    # 1 — Safimizga qo'shiling
    "Safimizga qo'shiling👇\nhttps://t.me/+Xa6LRjERxwo4Njdi\nhttps://t.me/+Xa6LRjERxwo4Njdi",
    # 2 — Talim_Live
    "Ta'lim tizimiga oid yangiliklar:\n➡️ @Talim_Live",
    # 3 — Talim24uz
    "✅️@Talim24uz",
    # 4 — (zaxira)
    "✅️@Talim24uz",
    # 5 — nodavlattalim_uz
    "👉 nodavlattalim.uz – rasmiy kanali",
    # 6 — Axmadjanovuz
    "👉 @Axmadjanovuz",
    # 7 — YANGI: abitur24 | Talim_Live | Talim24uz | ai_lingoBot
    "✔️ @mandatjavobbot orqali istalgan ta'lim yo'nalishlarining "
    "2025-2026-o'quv yilidagi o'tish ballari bilan tanishishingiz mumkin."
    "\n\n🖊 @BMB_testbot orqali maxsus diagnostik testlarni ishlab, "
    "o'z bilimingizni bepulga sinovdan o'tkazishingiz mumkin.",
    # 8 - botlar
    "🤳 @Ruxsatnoma2026_bot telegram-boti orqali Abituriyent ruxsatnomanisini yuklab olishi mumkin."
]


# ---------------------------------------------------------------------------
# CHANNEL_TEXTS — kanal → qo'shiladigan ALL_TEXT indekslari (tartibda)
#
# Bir kanalga bir nechta suffix qo'shish mumkin.
# tele.py _build_full_suffix() ularni ketma-ket birlashtiradi.
# ---------------------------------------------------------------------------
CHANNEL_TEXTS: dict[str, list[int]] = {
    "nodavlattalim":    [0],
    "abitur24":         [7, 8, 1],
    "Talim_Live":       [7, 8, 2],
    "Talim24uz":        [7, 8, 3],
    "Axmadjanovuz":     [6],
    "nodavlattalim_uz": [5],
    "ai_lingoBot":      [7, 8, 1],
}


# ---------------------------------------------------------------------------
# RAW_ENTITIES — matn BOSHIDAN 0-based UTF-16-LE unit offset'lar.
#
# entities_right(original_text, num) chaqirilganda base_offset avtomatik
# qo'shiladi: utf16(original_text) + 2  (tele.py "\n\n" separator = 2 unit).
#
# BARCHA offset va length'lar Python skript bilan tekshirildi ✓
# ---------------------------------------------------------------------------
RAW_ENTITIES: dict[int, list[dict]] = {

    # 0 — "🇺🇿 @nodavlattalim — nodavlat oliy ta'lim..."
    # 🇺🇿 = U+1F1FA + U+1F1FF (har biri surrogate pair) = 4 UTF-16 unit
    # " " = 1 unit → "@nodavlattalim" offset=5
    # "— nodavlat..." offset=20 (5+14+1=" ")
    0: [
        {"offset": 0,  "length": 4,  "type": "custom_emoji", "custom_emoji_id": "5325506731164312731"},
        {"offset": 5,  "length": 14, "type": "mention"},
        {"offset": 5,  "length": 14, "type": "bold"},
        {"offset": 20, "length": 59, "type": "bold"},   # FIX: 19→20, 60→59
    ],

    # 1 — "Safimizga qo'shiling👇\n..."
    # bold covers "Safimizga qo'shiling👇" = 20 chars + 👇(2 units) = 22 ✓
    1: [
        {"offset": 0, "length": 22, "type": "bold"},
    ],

    # 2 — "Ta'lim tizimiga oid yangiliklar:\n➡️ @Talim_Live"
    # "Ta'lim tizimiga oid yangiliklar:" = 32 UTF-16 units  FIX: 33→32
    # ➡️ = U+27A1(1) + U+FE0F(1) = 2 units → at offset 33
    # " " at 35 → "@Talim_Live" at 36                       FIX: 37→36
    2: [
        {"offset": 0,  "length": 32, "type": "bold"},    # FIX: 33→32
        {"offset": 36, "length": 11, "type": "mention"}, # FIX: 37→36
    ],

    # 3 — "✅️@Talim24uz"
    # ✅ = U+2705(1) + U+FE0F(1) = 2 units → "@Talim24uz" at 2
    3: [
        {"offset": 0, "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5350384878254826109"},
        {"offset": 2, "length": 10, "type": "mention"},
    ],

    # 4 — (zaxira, 3 bilan bir xil)
    4: [
        {"offset": 0, "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5350384878254826109"},
        {"offset": 2, "length": 10, "type": "mention"},
    ],

    # 5 — "👉 nodavlattalim.uz – rasmiy kanali"
    # 👉 = U+1F449 (surrogate) = 2 units, " " = 1 → "nodavlattalim.uz" at 3
    # "nodavlattalim.uz" = 16 UTF-16 units
    # Total text = 35 UTF-16 units → bold covers all (length=35)
    # FIX: mention entity OLIB TASHLANDI (text da @mention yo'q)
    5: [
        {"offset": 0, "length": 35, "type": "bold"},
        {"offset": 3, "length": 16, "type": "text_link", "url": "https://t.me/nodavlattalim_uz"},
    ],

    # 6 — "👉 @Axmadjanovuz"
    # 👉 = 2 units, " " = 1 → "@Axmadjanovuz" at 3, length=13  FIX: 14→13
    6: [
        {"offset": 3, "length": 13, "type": "mention"},  # FIX: 14→13
    ],

    # 7 — "✔️ @mandatjavobbot ... 🖊 @BMB_testbot ..."
    # Barcha offset'lar JSON bilan aynan mos (tekshirildi ✓)
    # FIX: italic "diagnostik..." length 84→85
    7: [
        # ✔️ = U+2714(1) + U+FE0F(1) = 2 units
        {"offset": 0,   "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5321210956414459578"},
        {"offset": 3,   "length": 15, "type": "mention"},
        {"offset": 3,   "length": 15, "type": "bold"},
        {"offset": 3,   "length": 15, "type": "italic"},
        {"offset": 18,  "length": 42, "type": "italic"},
        {"offset": 60,  "length": 39, "type": "bold"},
        {"offset": 60,  "length": 39, "type": "italic"},
        {"offset": 100, "length": 28, "type": "italic"},
        # 🖊 = U+1F58A (surrogate) = 2 units
        {"offset": 130, "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5321223519193800525"},
        {"offset": 132, "length": 1,  "type": "italic"},   # space after 🖊
        {"offset": 133, "length": 12, "type": "mention"},
        {"offset": 133, "length": 12, "type": "bold"},
        {"offset": 133, "length": 12, "type": "italic"},
        {"offset": 145, "length": 15, "type": "italic"},
        {"offset": 160, "length": 85, "type": "italic"},   # FIX: 84→85
        {"offset": 160, "length": 77, "type": "bold"},
    ],
    
    # 8 — "🤳 @Ruxsatnoma2026_bot ..."
    8: [
        {"offset": 0,  "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5319109506225938985"},
        {"offset": 44,  "length": 28, "type": "bold"},
        {"offset": 0,  "length": 94, "type": "italic"},
    ],
}


# ---------------------------------------------------------------------------
# Entity builder
# ---------------------------------------------------------------------------
def entities_right(original_text: str, num: int) -> list:
    """
    original_text — shu paytgacha yig'ilgan xabar matni.
    num           — ALL_TEXT / RAW_ENTITIES indeksi.

    base_offset hisoblash:
        original_text bo'sh  → 0
        bo'sh emas           → utf16(original_text) + 2
        (+2 = tele.py qo'shadigan "\\n\\n" = 2 UTF-16 unit)
    """
    if num not in RAW_ENTITIES:
        return []

    base_offset = (
        0 if not original_text
        else len(original_text.encode("utf-16-le")) // 2 + 2
    )

    final_entities: list = []
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