from telethon.tl.types import MessageEntityCustomEmoji

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


def entities_right(original_text: str, num: int):
    if num not in CUSTOM_EMOJI_MAP:
        return []

    emoji_length, emoji_id = CUSTOM_EMOJI_MAP[num]

    # new_text = original_text + '\n\n' + ALL_TEXT[num]
    # Demak, offset — bu original_text uzunligi + 2 (yangi qatordan)
    offset = len(original_text) + 2

    return [MessageEntityCustomEmoji(
        offset=offset,
        length=emoji_length,
        document_id=emoji_id
    )]