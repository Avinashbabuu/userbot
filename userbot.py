from telethon import TelegramClient, events
from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
dest_channel_id = int(os.getenv("DEST_CHANNEL_ID"))

client = TelegramClient('session', api_id, api_hash)

filters = {}

@client.on(events.NewMessage(outgoing=True, pattern='/start'))
async def start_handler(event):
    await event.reply("Welcome to the UserBot!\nCommands:\n/filter\n/delfilter\nWord replacement works in auto-forwarding.")

@client.on(events.NewMessage(outgoing=True, pattern='/filter'))
async def filter_handler(event):
    await event.reply("Send word pair like this: `Hi==Hello`", parse_mode='markdown')

@client.on(events.NewMessage(outgoing=True, pattern=r'^[^\n=]+==[^\n=]+$'))
async def add_filter(event):
    try:
        original, replacement = event.raw_text.split("==", 1)
        filters[original.strip()] = replacement.strip()
        await event.reply(f"Filter added: '{original.strip()}' will be replaced with '{replacement.strip()}'")
    except:
        await event.reply("Invalid format. Use: Hi==Hello")

@client.on(events.NewMessage(outgoing=True, pattern='/delfilter'))
async def del_filter(event):
    if not filters:
        await event.reply("No filters set.")
        return
    msg = "Filters:\n" + "\n".join([f"{i+1}. {k} => {v}" for i, (k, v) in enumerate(filters.items())])
    await event.reply(msg + "\n\nReply with the number to delete that filter.")

@client.on(events.NewMessage(outgoing=True))
async def del_filter_number(event):
    if event.reply_to_msg_id:
        try:
            num = int(event.raw_text.strip()) - 1
            key = list(filters.keys())[num]
            del filters[key]
            await event.reply(f"Deleted filter {num+1}: {key}")
        except:
            pass

@client.on(events.NewMessage(chats=None))
async def forward_and_replace(event):
    if event.chat_id == dest_channel_id:
        return

    text = event.raw_text
    for k, v in filters.items():
        text = text.replace(k, v)

    if event.media:
        await client.send_file(dest_channel_id, file=event.media, caption=text)
    else:
        await client.send_message(dest_channel_id, text)

client.start()
print("UserBot running...")
client.run_until_disconnected()
