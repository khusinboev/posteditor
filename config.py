from kurigram import CustomEmoji
from kurigram.enums import EmojiPosition

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

def entities_right(original_text: str, num: int):
    if num not in CUSTOM_EMOJI_MAP:
        return []

    emoji_length, emoji_id = CUSTOM_EMOJI_MAP[num]

    # kurigram yordamida emoji ni tuzish
    emoji = CustomEmoji(
        document_id=emoji_id,
        length=emoji_length,
        position=EmojiPosition.NEW_LINE_AFTER_TEXT  # yangi qatordan qo'shish
    )

    # emoji'ni tuzib, entity sifatida qaytarish
    return emoji.build_entities(original_text)