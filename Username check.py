import asyncio
import re
import os
from telethon import TelegramClient
from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError, FloodWaitError

# ==============================
# 🔧 CONFIG FILE SYSTEM
# ==============================
CONFIG_FILE = "config.txt"
SESSION_NAME = "username_checker"
USERNAME_FILE = "usernames.txt"
OUTPUT_FILE = "available.txt"

def load_config():
    """Load saved API credentials if exist."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            lines = [x.strip() for x in f.readlines()]
            if len(lines) >= 2:
                return int(lines[0]), lines[1]
    return None, None

def save_config(api_id, api_hash):
    """Save API credentials for future use."""
    with open(CONFIG_FILE, "w") as f:
        f.write(f"{api_id}\n{api_hash}\n")
    print("✅ API credentials saved! You won't have to enter them again.\n")

# ==============================
# 🔹 VALIDATION
# ==============================
USERNAME_REGEX = re.compile(r'^[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]$')

async def is_valid_username(username):
    username = username.lstrip('@')
    return bool(USERNAME_REGEX.match(username)) and 5 <= len(username) <= 32

async def check_username(client, username):
    username = username.lstrip('@')
    if not await is_valid_username(username):
        return f"{username} -> INVALID (regex fail or length issue)"
    try:
        await client.get_entity(f"@{username}")
        return f"{username} -> TAKEN"
    except UsernameNotOccupiedError:
        return f"{username} -> AVAILABLE"
    except UsernameInvalidError:
        return f"{username} -> INVALID (Telegram rule)"
    except FloodWaitError as e:
        wait_time = e.seconds
        print(f"⚠️ FloodWait: Waiting {wait_time} seconds...")
        await asyncio.sleep(wait_time)
        return f"{username} -> WAITED ({wait_time}s)"
    except Exception as e:
        return f"{username} -> ERR {str(e)}"

# ==============================
# 🔹 MAIN PROGRAM
# ==============================
async def main():
    print("🔹 Telegram Username Checker")

    api_id, api_hash = load_config()
    if not api_id or not api_hash:
        try:
            api_id = int(input("Enter API ID: "))
            api_hash = input("Enter API HASH: ").strip()
            save_config(api_id, api_hash)
        except ValueError:
            print("❌ ERROR: API ID must be a number.")
            return

    client = TelegramClient(SESSION_NAME, api_id, api_hash)
    await client.start()

    try:
        with open(USERNAME_FILE, "r") as f:
            usernames = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ ERROR: {USERNAME_FILE} not found.")
        return

    available = []
    total = len(usernames)
    print(f"🔍 Checking {total} usernames...\n")

    for i, username in enumerate(usernames, 1):
        result = await check_username(client, username)
        print(f"{i}/{total} {result}")
        if "AVAILABLE" in result:
            available.append(username.lstrip('@'))
        await asyncio.sleep(1)

    with open(OUTPUT_FILE, "w") as f:
        for uname in available:
            f.write(uname + "\n")

    print(f"\n✅ Done! {len(available)} available usernames saved in {OUTPUT_FILE}.")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
