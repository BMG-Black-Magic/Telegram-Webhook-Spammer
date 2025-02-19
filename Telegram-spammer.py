import os
import requests
import time
import re
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SCRIPT_FILE = os.getenv("SCRIPT_FILE", "Bee.txt")
SEND_MESSAGE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
RATE_LIMIT = 1

def send_message(text, progress_bar=None):
    while True:
        try:
            response = requests.post(SEND_MESSAGE_URL, json={"chat_id": CHAT_ID, "text": text})
            data = response.json()
            
            if response.status_code == 200:
                if progress_bar:
                    progress_bar.update(1)
                return
            elif response.status_code == 429:
                retry_after = data.get("parameters", {}).get("retry_after", 5)
                print(f"\n⚠️ Rate limited! Waiting {retry_after} seconds...\n")
                time.sleep(retry_after)
            else:
                print(f"\n❌ Error {response.status_code}: {response.text}\n")
                break
        except requests.RequestException as e:
            print(f"\n❌ Request failed: {e}\n")
            time.sleep(5)

def extract_lines(script_text):
    lines = script_text.split("\n")
    dialogue_list = []
    character = None

    for line in lines:
        line = line.strip()

        if line.startswith("(") and line.endswith(")"):
            continue

        if re.match(r"^[A-Z\s]+:$", line):
            character = line[:-1].strip()
        elif character and line and line != ":":
            dialogue_list.append(f"**{character}**: {line}")

    return dialogue_list

def send_script(dialogue_list):
    total_messages = len(dialogue_list)
    print(f"📤 Sending {total_messages} messages...\n")

    with tqdm(total=total_messages, desc="🚀 Progress", unit="msg") as progress_bar:
        for message in dialogue_list:
            send_message(message, progress_bar)
            time.sleep(RATE_LIMIT)

def main():
    print("📖 Reading Bee Movie script from file...")

    try:
        with open(SCRIPT_FILE, "r", encoding="utf-8") as file:
            script_text = file.read().strip()
        
        print("🔍 Extracting character dialogues...")
        dialogue_list = extract_lines(script_text)
        
        if not dialogue_list:
            print("⚠️ No dialogue detected! Check the script format.")
        else:
            send_script(dialogue_list)
    except FileNotFoundError:
        print(f"❌ Error: File '{SCRIPT_FILE}' not found!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError("Missing required environment variables: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
    main()
