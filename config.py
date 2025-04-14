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

def entities_right(msg, num):
    # Emoji o'lchamlarini hisoblash va to'g'ri joylash
    en = len(msg) if len(msg) == 0 else len(msg) + 2 + len([char for char in msg if emoji.is_emoji(char)])
    print("Emoji uzunligi:", en)

    ALL_ENTITIES = [
        [  # 0-index: 🇺🇿
            MessageEntityCustomEmoji(
                offset=en,
                length=4,
                document_id=5325506731164312731  # Emoji document_id
            )
        ],
        None,  # 1
        None,  # 2
        [  # 3
            MessageEntityCustomEmoji(
                offset=en,
                length=2,
                document_id=5350384878254826109
            )
        ],
        [  # 4
            MessageEntityCustomEmoji(
                offset=en,
                length=2,
                document_id=5350384878254826109
            )
        ],
        None
    ]
    return ALL_ENTITIES[num]