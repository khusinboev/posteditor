from telethon.tl.types import (
    MessageEntityMention,
    MessageEntityBold,
    MessageEntityTextUrl,
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
        {"offset": 0, "length": 33, "type": "bold"},
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
