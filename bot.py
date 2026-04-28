import os
import requests
from bs4 import BeautifulSoup
from atproto import Client

URL = "https://whatsonnow.criterionchannel.com/"
STATE_FILE = "last_seen.txt"

BSKY_HANDLE = os.environ["BSKY_HANDLE"]
BSKY_APP_PASSWORD = os.environ["BSKY_APP_PASSWORD"]


def get_current_title():
    html = requests.get(URL, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for i, line in enumerate(lines):
        # Look specifically for "now:" and grab the next line
        if line.lower() == "now:" and i + 1 < len(lines):
            return lines[i + 1]

    raise ValueError("Could not find current title")


def read_last_seen():
    if not os.path.exists(STATE_FILE):
        return None

    with open(STATE_FILE, "r") as file:
        return file.read().strip()


def write_last_seen(title):
    with open(STATE_FILE, "w") as file:
        file.write(title)


def post_to_bluesky(title):
    client = Client()
    client.login(BSKY_HANDLE, BSKY_APP_PASSWORD)

    post = f"""🎬 Now playing on Criterion 24/7:

{title}

{URL}"""

    client.send_post(post)


def main():
    current_title = get_current_title()
    last_seen = read_last_seen()

    if current_title != last_seen:
        post_to_bluesky(current_title)
        write_last_seen(current_title)
        print(f"Posted: {current_title}")
    else:
        print(f"No change: {current_title}")


if __name__ == "__main__":
    main()
