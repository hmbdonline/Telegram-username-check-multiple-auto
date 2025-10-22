import asyncio
import re
from telethon import TelegramClient
from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError, UsernameOccupiedError, FloodWaitError

# Regex for Telegram username validation
USERNAME_REGEX = re.compile(r'^[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]$')

async def is_valid_username(username):
    """Pre-check if username matches Telegram regex."""
    username = username.lstrip('@')  # Remove @ if present
    return bool(USERNAME_REGEX.match(username)) and 5 <= len(username) <= 32

async def check_username(client, username):
    """Check if a username is available, taken, or invalid."""
    username = username.lstrip('@')  # Remove @ if present
    if not await is_valid_username(username):
        return f"{username} -> INVALID (regex fail or length issue)"

    try:  
        # Try to resolve the username to an entity (user, channel, or bot)  
        entity = await client.get_entity(f"@{username}")  
        return f"{username} -> TAKEN"  
    except UsernameNotOccupiedError:  
        return f"{username} -> AVAILABLE"  
    except UsernameInvalidError:  
        return f"{username} -> INVALID (Telegram rule)"  
    except ValueError as e:  
        if "No user has" in str(e):  
            return f"{username} -> AVAILABLE"  
        return f"{username} -> ERR {str(e)}"  
    except FloodWaitError as e:  
        wait_time = e.seconds  
        print(f"Rate limit hit, waiting {wait_time} seconds...")  
        await asyncio.sleep(wait_time)  
        return f"{username} -> ERR Rate limit, try again later"  
    except Exception as e:  
        return f"{username} -> ERR {str(e)}"

async def main():
    # Input API credentials
    try:
        api_id = int(input('Enter API ID: '))
        api_hash = input('Enter API HASH: ')
    except ValueError:
        print("ERROR: API ID must be a number.")
        return

    # Initialize Telegram client  
    client = TelegramClient('session_check', api_id, api_hash)  

    try:  
        await client.start()  
    except Exception as e:  
        print(f"Authentication failed: {str(e)}")  
        return  

    # Read usernames from file  
    try:  
        with open('usernames.txt', 'r') as f:  
            usernames = [line.strip() for line in f if line.strip()]  
    except FileNotFoundError:  
        print("ERROR: usernames.txt not found.")  
        return  

    available = []  
    total = len(usernames)  

    # Check each username  
    for i, username in enumerate(usernames, 1):  
        result = await check_username(client, username)  
        print(f"{i}/{total} {result}")  

        if "AVAILABLE" in result:  
            available.append(username.lstrip('@'))  

        # Rate limit avoidance: 1-second delay  
        await asyncio.sleep(1)  

    # Save available usernames to file  
    try:  
        with open('available.txt', 'w') as f:  
            for uname in available:  
                f.write(uname + '\n')  
        print("Finished! Available usernames are saved in available.txt.")  
    except Exception as e:  
        print(f"ERROR: Could not write to available.txt: {str(e)}")  

    # Disconnect client  
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
