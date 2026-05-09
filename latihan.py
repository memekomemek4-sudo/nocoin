import requests
import time
import sys
import json
import os

BASE_URL = "https://bqrapnlqqtjedjyhlfci.supabase.co/functions/v1"

ETH = "0x16b61728424dE810C8301aD77Bae1Dbd997fce07"
AGENT = "kimi"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJxcmFwbmxxcXRqZWRqeWhsZmNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgyNzUyNjQsImV4cCI6MjA5Mzg1MTI2NH0.mf0fz6kAnK0yeAXrb-XT6yikbdRmeAq5jsikVPPhaFE"

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

STATE_FILE = "state.json"


def save_state(running):
    with open(STATE_FILE, "w") as f:
        json.dump({"running": running}, f)


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"running": False}
    with open(STATE_FILE) as f:
        return json.load(f)


from google import genai

client = genai.Client(api_key="AIzaSyCmedwmq5XgsHgwM9epD6ksa2Bew9HEUfc")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="halo"
)

print(response.text)

def get_puzzle():
    url = f"{BASE_URL}/submit-solution?eth={ETH}"
    r = requests.get(url, headers=HEADERS)
    print("RAW RESPONSE:", r.text)  # <- TAMBAH INI
    return r.json()


def solve(puzzle):
    prompt = puzzle.get("prompt", "")
    return prompt.lower().strip()


def submit(puzzle_id, answer):
    url = f"{BASE_URL}/submit-solution"

    data = {
        "eth_address": ETH,
        "agent_name": AGENT,
        "puzzle_id": puzzle_id,
        "answer": answer
    }

    r = requests.post(url, json=data, headers=HEADERS)
    return r.json()


def run():
    print("🚀 NoCoin Miner Started...")

    save_state(True)

    while True:
        state = load_state()
        if not state.get("running"):
            print("🛑 Stopped.")
            break

        try:
            data = get_puzzle()
            puzzle = data.get("puzzle")

            if not puzzle:
                print("⏳ No puzzle found...")
                time.sleep(3)
                continue

            print(f"📦 Puzzle ID: {puzzle['id']}")

            answer = solve(puzzle)
            result = submit(puzzle["id"], answer)

            print("✅ Result:", result)

            time.sleep(2)

        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(5)


def stop():
    save_state(False)
    print("🛑 Miner stopped")


def status():
    state = load_state()
    print("📊 Running:" , state.get("running", False))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
Usage:
  python3 nocoin.py run
  python3 nocoin.py stop
  python3 nocoin.py status
""")
        sys.exit()

    cmd = sys.argv[1]

    if cmd == "run":
        run()
    elif cmd == "stop":
        stop()
    elif cmd == "status":
        status()
    else:
        print("Unknown command")
