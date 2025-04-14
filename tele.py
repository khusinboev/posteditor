from telethon import TelegramClient, events
from config import API_ID, API_HASH, SESSION_NAME, admin, ALL_ID, ALL_TEXT, entities_right

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage())
async def handler(event):
    if event.chat and event.chat.username in ALL_ID:
        if event.sender_id not in admin:
            return

        try:
            num = ALL_ID.index(event.chat.username)
            original_text = event.raw_text
            extra_text = ALL_TEXT[num]
            final_text = original_text + "\n\n" + extra_text

            await client.edit_message(
                entity=event.chat_id,
                message=event.message.id,
                text=final_text,
                entities=entities_right(original_text, num)
            )
        except Exception as e:
            print("Xatolik:", e)

client.start()
client.run_until_disconnected()