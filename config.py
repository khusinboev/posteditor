from telethon.tl.types import MessageEntityCustomEmoji

API_ID = 29595868
API_HASH = 'a09a969ce2b4e13726812ab8e696cd18'
SESSION_NAME = 'my_bot'

admin = [619839487, 1918760732]

ALL_ID = [
    "nodavlattalim",
    "abitur24",
    "Talim_Live",
    "Talim24uz",
    "ai_lingoBot",
    "TRANSLATE_TRANSLATOR_PEREVODCHIK"
]

ALL_TEXT = [
    "🇺🇿 @nodavlattalim — nodavlat oliy ta’lim muassasalari haqida rasmiy xabarlar!",
    "Safimizga qo'shiling👇\nhttps://t.me/+Xa6LRjERxwo4Njdi",
    "Ta‘lim tizimiga oid yangiliklar:\n➡️ @Talim_Live",
    "✅️@Talim24uz",
    "✅️@Talim24uz",
    "Ta‘lim tizimiga oid yangiliklar:\n➡️ @Talim_Live"
]

def entities_right(msg: str, num: int):
    added_text = ALL_TEXT[num]
    full_text = msg + "\n\n" + added_text

    emoji_data = {
        0: ("🇺🇿", 5325506731164312731, 4),
        3: ("✅️", 5350384878254826109, 2),
        4: ("✅️", 5350384878254826109, 2)
    }

    if num not in emoji_data:
        return None

    emoji_char, doc_id, emoji_len = emoji_data[num]
    offset = full_text.find(emoji_char)

    if offset == -1:
        print(f"Emoji '{emoji_char}' not found in the text!")
        return None

    return [
        MessageEntityCustomEmoji(
            offset=offset,
            length=emoji_len,
            document_id=doc_id
        )
    ]