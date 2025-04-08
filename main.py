from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, SESSION_NAME, ALL_ID
from utils import is_original_post, edit_text_message, edit_caption_message, from_bot

app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH
)

@app.on_message(filters.chat(ALL_ID) & filters.incoming)
async def handle_new_message(client: Client, message: Message):
    """Handle new messages in the channel"""
    with open("data.txt", "r", encoding='utf-8') as file:
        content = file.read()
    print(content)
    if is_original_post(message) and content == "/start":
        if message.text:
            await edit_text_message(client, message, ALL_ID.index(message.chat.id))
        elif message.caption or (message.media and not message.text):
            await edit_caption_message(client, message, ALL_ID.index(message.chat.id))


if __name__ == "__main__":
    app.run()