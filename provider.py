#!/usr/bin/env python3

import json
import logging
import ssl
from urllib.request import urlopen

JSON_URL = (
    "https://raw.githubusercontent.com/"
    "darkbyteprojects/iptv_png/main/provider_1/sports_channels.json"
)

M3U_FILE = "stv10.m3u"
LOG_FILE = "stv10.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


def get_field(item, keys, default=""):
    for key in keys:
        value = item.get(key)
        if value:
            return str(value)
    return default


def load_json(url):
    ctx = ssl.create_default_context()

    with urlopen(url, context=ctx, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_data(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in [
            "channels",
            "data",
            "items",
            "results",
            "sports_channels"
        \]:
            if key in data and isinstance(data[key], list):
                return data[key]

    raise ValueError("Unsupported JSON structure")


def main():
    logging.info("Downloading JSON")

    data = load_json(JSON_URL)
    channels = normalize_data(data)

    logging.info("Loaded %s records", len(channels))

    written = 0

    with open(M3U_FILE, "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n")

        for item in channels:

            if not isinstance(item, dict):
                continue

            name = get_field(
                item,
                ["name", "title", "channel_name"],
                "Unknown"
            )

            logo = get_field(
                item,
                ["logo", "logo_url", "image", "thumbnail"],
                ""
            )

            group = get_field(
                item,
                ["group", "category", "group_title"],
                "Sports"
            )

            stream = get_field(
                item,
                [
                    "url",
                    "stream_url",
                    "stream",
                    "play_url",
                    "source",
                    "link"
                ]
            )

            if not stream:
                logging.warning("Skipped: %s", name)
                continue

            m3u.write(
                f'#EXTINF:-1 tvg-name="{name}" '
                f'tvg-logo="{logo}" '
                f'group-title="{group}",{name}\n'
            )

            m3u.write(stream + "\n")

            written += 1

    logging.info("Written channels: %s", written)
    print(f"SUCCESS: {written} channels written to {M3U_FILE}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.exception("Fatal error")
        print("ERROR:", exc)
        raise
