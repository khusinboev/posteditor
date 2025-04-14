from telethon.tl.types import MessageEntityCustomEmoji
import emoji

API_ID = 29595868
API_HASH = 'a09a969ce2b4e13726812ab8e696cd18'
SESSION_NAME = 'my_bot'  # Session name for the user bot

admin = [619839487, 1918760732]

ALL_ID = ["nodavlattalim",
          "abitur24",
          "Talim_Live",
          "Talim24uz",
          "ai_lingoBot",
          "TRANSLATE_TRANSLATOR_PEREVODCHIK"]

ALL_TEXT = [
    "🇺🇿 @nodavlattalim — nodavlat oliy ta’lim muassasalari haqida rasmiy xabarlar!",
    "Safimizga qo'shiling👇\nhttps://t.me/+Xa6LRjERxwo4Njdi",
    "Ta‘lim tizimiga oid yangiliklar:\n➡️ @Talim_Live",
    "✅️@Talim24uz",
    "✅️@Talim24uz",
    "Ta‘lim tizimiga oid yangiliklar:\n➡️ @Talim_Live"
]

def entities_right(msg: str, num: int):
    added_text = "\n\n" + ALL_TEXT[num]  # Biz qo‘shayotgan matn
    full_text = msg + added_text

    # Qayerga emoji qo‘shilishini aniqlaymiz
    emoji_pos = full_text.find('🇺🇿') if '🇺🇿' in full_text else full_text.find('✅️')

    if emoji_pos == -1:
        return None

    # Emoji uzunligini aniqlash
    emoji_len = 4 if '🇺🇿' in full_text else 2

    ALL_ENTITIES = {
        0: [
            MessageEntityCustomEmoji(
                offset=emoji_pos,
                length=emoji_len,
                document_id=5325506731164312731
            )
        ],
        3: [
            MessageEntityCustomEmoji(
                offset=emoji_pos,
                length=emoji_len,
                document_id=5350384878254826109
            )
        ],
        4: [
            MessageEntityCustomEmoji(
                offset=emoji_pos,
                length=emoji_len,
                document_id=5350384878254826109
            )
        ]
    }

    return ALL_ENTITIES.get(num, None)