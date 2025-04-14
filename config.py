from telethon.tl.types import (
    MessageEntityBold,
    MessageEntityMention,
    MessageEntityUrl,
    MessageEntityCustomEmoji
)
import logging

# Loggingni sozlash
logging.basicConfig(level=logging.INFO, filename="bot_log.txt",
                    format="%(asctime)s - %(levelname)s - %(message)s")

def log_error(message):
    logging.error(message)

def log_info(message):
    logging.info(message)

# API sozlamalari
API_ID = 29595868
API_HASH = 'a09a969ce2b4e13726812ab8e696cd18'
SESSION_NAME = 'my_bot'

# Adminlar
admin = [619839487, 1918760732]

# Telegram kanal identifikatorlari
ALL_ID = ["nodavlattalim", "abitur24", "Talim_Live", "Talim24uz", "ai_lingoBot", "TRANSLATE_TRANSLATOR_PEREVODCHIK"]

# Kanalga qo'shilgan matnlar
ALL_TEXT = [
    "🇺🇿 @nodavlattalim — nodavlat oliy ta’lim muassasalari haqida rasmiy xabarlar!",
    "Safimizga qo'shiling👇\nhttps://t.me/+Xa6LRjERxwo4Njdi",
    "Ta‘lim tizimiga oid yangiliklar:\n➡️ @Talim_Live",
    "✅️@Talim24uz",
    "✅️@Talim24uz",
    "Ta‘lim tizimiga oid yangiliklar:\n➡️ @Talim_Live"
]

# Har bir maxsus emoji uchun offset va id
CUSTOM_EMOJI_MAP = {
    0: (4, 5325506731164312731),  # 🇺🇿
    3: (2, 5350384878254826109),  # ✅
    4: (2, 5350384878254826109),  # ✅
}

# Matnga mos holda entity obyektlarini yaratish
def entities_right(original_text: str, num: int):
    if num not in CUSTOM_EMOJI_MAP:
        return []

    emoji_length, emoji_id = CUSTOM_EMOJI_MAP[num]
    offset = 0 if len(original_text) == 0 else len(original_text.encode('utf-16-le')) // 2 + 2

    return [MessageEntityCustomEmoji(
        offset=offset,
        length=emoji_length,
        document_id=emoji_id
    )]

# JSONdan kelgan entitylarni Telethon formatiga o‘tkazuvchi funksiya
def parse_entities_from_json(json_entities):
    entity_objects = []
    for ent in json_entities:
        offset = ent.get("offset", 0)
        length = ent.get("length", 0)
        etype = ent.get("type")

        if etype == "bold":
            entity_objects.append(MessageEntityBold(offset=offset, length=length))
        elif etype == "mention":
            entity_objects.append(MessageEntityMention(offset=offset, length=length))
        elif etype == "url":
            entity_objects.append(MessageEntityUrl(offset=offset, length=length))
        elif etype == "custom_emoji":
            emoji_id = int(ent.get("custom_emoji_id", 0))
            entity_objects.append(MessageEntityCustomEmoji(
                offset=offset,
                length=length,
                document_id=emoji_id
            ))

    return entity_objects