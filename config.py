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


# ---------------------------------------------------------------------------
# API sozlamalari
# ---------------------------------------------------------------------------
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
# ALL_TEXT — qo'shiladigan matnlar (indeks = kalit)
#
# FIX: ALL_TEXT[7] boshidagi "\n\n" OLIB TASHLANDI.
#   Sabab: tele.py da suffix qo'shilganda
#     new_text = f"{original_text}\n\n{suffix}"
#   deb yoziladi. Agar suffix ham "\n\n" bilan boshlansa → 4 ta \n bo'lar edi.
#   entities_right() separator uchun +2 offset hisoblaydi — bu tele.py dagi
#   "\n\n" separator bilan mos. Shuning uchun suffix o'zida "\n\n" bo'lmasligi kerak.
# ---------------------------------------------------------------------------
ALL_TEXT: list[str] = [
    # 0
    "🇺🇿 @nodavlattalim — nodavlat oliy ta'lim muassasalari haqida rasmiy xabarlar!",
    # 1  — "Safimizga qo'shiling"
    "Safimizga qo'shiling👇\nhttps://t.me/+Xa6LRjERxwo4Njdi\nhttps://t.me/+Xa6LRjERxwo4Njdi",
    # 2  — Talim_Live
    "Ta'lim tizimiga oid yangiliklar:\n➡️ @Talim_Live",
    # 3  — Talim24uz
    "✅️@Talim24uz",
    # 4  — (zaxira, index 3 bilan bir xil, saqlab qolindi)
    "✅️@Talim24uz",
    # 5  — nodavlattalim_uz (text_link bilan)
    "👉 nodavlattalim.uz – rasmiy kanali",
    # 6  — Axmadjanovuz
    "👉 @Axmadjanovuz",
    # 7  — abitur24 | Talim_Live | Talim24uz | ai_lingoBot — YANGI (premium emoji)
    #   "\n\n" YO'Q — tele.py separator qo'shadi
    "✔️ @mandatjavobbot orqali istalgan ta'lim yo'nalishlarining "
    "2025-2026-o'quv yilidagi o'tish ballari bilan tanishishingiz mumkin."
    "\n\n🖊 @BMB_testbot orqali maxsus diagnostik testlarni ishlab, "
    "o'z bilimingizni bepulga sinovdan o'tkazishingiz mumkin.",
]


# ---------------------------------------------------------------------------
# CHANNEL_TEXTS — har bir kanalga qaysi ALL_TEXT indeks'lari qo'shilishini belgilaydi.
#
# Muhim: indeks'lar QO'SHILISH TARTIBIDA berilgan.
#   - tele.py har bir indeksni ketma-ket original xabarga append qiladi.
#   - entities_right(original_text, idx) chaqirilganda original_text
#     shu paytgacha yig'ilgan matn bo'ladi (offset to'g'ri hisoblangani uchun).
#
# Agar kanal ALL_ID da bo'lsa lekin bu dict da bo'lmasa → xabar tahrirlanmaydi.
# ---------------------------------------------------------------------------
CHANNEL_TEXTS: dict[str, list[int]] = {
    "nodavlattalim":    [0, 1],   # 🇺🇿 xabar + Safimizga
    "abitur24":         [7, 1],   # YANGI premium + Safimizga
    "Talim_Live":       [7, 2],   # YANGI premium + @Talim_Live
    "Talim24uz":        [7, 3],   # YANGI premium + ✅️@Talim24uz
    "Axmadjanovuz":     [6],      # 👉 @Axmadjanovuz
    "nodavlattalim_uz": [5],      # nodavlattalim.uz link
    "ai_lingoBot":      [7, 1],   # YANGI premium + Safimizga
}


# ---------------------------------------------------------------------------
# RAW_ENTITIES — entity'lar (offset'lar matn BOSHIDAN, 0-based UTF-16-LE unit)
#
# FIX: RAW_ENTITIES[7] offset'lari endi JSON bilan bir xil (0-based).
#   Avval "\n\n" prefix uchun +2 qo'shilgan edi — endi prefix yo'q, shuning uchun
#   entities_right() dagi base_offset (+2 separator) to'g'ri ishlaydi.
# ---------------------------------------------------------------------------
RAW_ENTITIES: dict[int, list[dict]] = {
    # 0 — 🇺🇿 @nodavlattalim
    0: [
        {"offset": 0,  "length": 4,  "type": "custom_emoji", "custom_emoji_id": "5325506731164312731"},
        {"offset": 5,  "length": 14, "type": "mention"},
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
        {"offset": 37, "length": 11, "type": "mention"},
    ],
    # 3 — ✅️@Talim24uz
    3: [
        {"offset": 0, "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5350384878254826109"},
        {"offset": 2, "length": 10, "type": "mention"},
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
    #   Offset'lar JSON bilan aynan bir xil (0-based, "\n\n" prefix yo'q).
    #   Tekshirilgan: barcha offset'lar Python skript bilan verified ✓
    7: [
        # ✔️  (U+2714 + U+FE0F, 1+1 UTF-16 unit → length=2)
        {"offset": 0,   "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5321210956414459578"},
        # @mandatjavobbot
        {"offset": 3,   "length": 15, "type": "mention"},
        {"offset": 3,   "length": 15, "type": "bold"},
        {"offset": 3,   "length": 15, "type": "italic"},
        # " orqali istalgan ta'lim yo'nalishlarining "
        {"offset": 18,  "length": 42, "type": "italic"},
        # "2025-2026-o'quv yilidagi o'tish ballari"
        {"offset": 60,  "length": 39, "type": "bold"},
        {"offset": 60,  "length": 39, "type": "italic"},
        # "bilan tanishishingiz mumkin."
        {"offset": 100, "length": 28, "type": "italic"},
        # 🖊  (U+1F58A, surrogate pair → length=2)
        {"offset": 130, "length": 2,  "type": "custom_emoji", "custom_emoji_id": "5321223519193800525"},
        # " " space after 🖊
        {"offset": 132, "length": 1,  "type": "italic"},
        # @BMB_testbot
        {"offset": 133, "length": 12, "type": "mention"},
        {"offset": 133, "length": 12, "type": "bold"},
        {"offset": 133, "length": 12, "type": "italic"},
        # " orqali maxsus "
        {"offset": 145, "length": 15, "type": "italic"},
        # "diagnostik testlarni ishlab, o'z bilimingizni bepulga sinovdan o'tkazishingiz mumkin."
        {"offset": 160, "length": 84, "type": "italic"},
        {"offset": 160, "length": 77, "type": "bold"},
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
        (+2 = tele.py da qo'shiladigan '\\n\\n' separator = 2 UTF-16 unit)
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