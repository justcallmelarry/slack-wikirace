import json
import os
import random

import requests
from yarl import URL


def send_slack_message(title=None, description=None, url=None) -> None:
    data = {
        "username": "WikiRace Daily Challenge",
        "icon_emoji": ":mortar_board:",
        "link_names": 1,
        "attachments": [
            {
                "title": f"Starting Point: {title}",
                "text": description,
                "color": "good",
            },
            {
                "title": f"Target: {get_target()}",
                "text": "Try to get from the article to the target in the least amount of clicks. React with how many click you got today!",
                "color": "white",
                "actions": [
                    {
                        "text": "Start racing!",
                        "type": "button",
                        "url": url,
                        "style": "primary",
                    }
                ],
            },
        ],
    }
    project_path = os.path.dirname(__file__)
    with open(os.path.join(project_path, "settings.json")) as settings_file:
        settings = json.load(settings_file)
        for slack in settings.values():
            data["channel"] = slack.get("channel")
            requests.post(slack.get("hook"), data=json.dumps(data))


def get_target() -> str:
    with open("targets.txt") as file:
        targets = file.read().splitlines()

    return random.choice(targets)


def main() -> None:
    site = requests.get("https://en.wikipedia.org/wiki/Special:Random")
    url = URL(site.url)
    title = url.path.replace("/wiki/", "")

    params = {
        "format": "json",
        "action": "query",
        "prop": "extracts",
        "explaintext": "1",
        "titles": title,
    }
    actual_site = requests.get("http://en.wikipedia.org/w/api.php", params=params)
    body = actual_site.json()
    page = list(body.get("query").get("pages").values())[0]
    title = page.get("title")
    try:
        extract = page.get("extract").split("\n\n", 1)[0]
    except Exception:
        extract = page.get("extract")[0:34] + "…"
    send_slack_message(title=title, description=extract, url=site.url)


if __name__ == "__main__":
    main()
