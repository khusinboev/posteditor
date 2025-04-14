from telethon.tl.types import MessageEntityCustomEmoji
import emoji
import re

API_ID = 29595868
API_HASH = 'a09a969ce2b4e13726812ab8e696cd18'
SESSION_NAME = 'my_bot'

admin = [619839487, 1918760732]

ALL_ID = ["nodavlattalim", "abitur24", "Talim_Live", "Talim24uz", "ai_lingoBot", "TRANSLATE_TRANSLATOR_PEREVODCHIK"]

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

def calc_true_offset(msg: str):
    """Matnda emoji'lar joylashgan joyni aniqlash"""
    # Emoji'lar ro'yxatini olish uchun Unicode emoji belgilari ishlatish
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]")
    emojis = emoji_pattern.findall(msg)
    return len(emojis)

def entities_right(original_text: str, num: int):
    """Maxsus emoji uchun entity yaratish"""
    if num not in CUSTOM_EMOJI_MAP:
        return []

    emoji_length, emoji_id = CUSTOM_EMOJI_MAP[num]

    # offset: matnning real uzunligi + emoji soni + 2 (yangi qator uchun)
    offset = len(original_text) + calc_true_offset(original_text) + 2

    return [MessageEntityCustomEmoji(
        offset=offset,
        length=emoji_length,
        document_id=emoji_id
    )]