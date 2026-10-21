#!/usr/bin/env python3

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen

import requests

JSON_URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_5/live_events.json"

M3U_FILE = "stv10.m3u"
LOG_FILE = "stv10.log"

MAX_WORKERS = 50

_thread_local = threading.local()


def get_session():
    if not hasattr(_thread_local, "session"):
        session = requests.Session()

        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/130.0 Safari/537.36"
            )
        })

        _thread_local.session = session

    return _thread_local.session


def normalize_drm_key(drm_key):
    if not drm_key:
        return ""

    if isinstance(drm_key, str):
        drm_key = drm_key.strip()

        if ":" in drm_key and not drm_key.startswith("{"):
            return drm_key

        if drm_key.startswith("{"):
            try:
                obj = json.loads(drm_key)

                if "keys" in obj and obj["keys"]:
                    item = obj["keys"][0]

                    kid = item.get("kid", "")
                    key = item.get("k", "")

                    if kid and key:
                        return f"{kid}:{key}"

            except Exception:
                pass

    elif isinstance(drm_key, dict):

        if "keys" in drm_key and drm_key["keys"]:
            item = drm_key["keys"][0]

            kid = item.get("kid", "")
            key = item.get("k", "")

            if kid and key:
                return f"{kid}:{key}"

    return ""


def write_kodiprop(fp, url, drm_scheme, drm_key):

    drm_key = normalize_drm_key(drm_key)

    if not drm_key:
        return

    if (drm_scheme or "").lower() != "clearkey":
        return

    manifest_type = "mpd"

    if ".m3u8" in url.lower():
        manifest_type = "hls"

    fp.write("#KODIPROP:inputstream=inputstream.adaptive\n")
    fp.write(
        f"#KODIPROP:inputstream.adaptive.manifest_type={manifest_type}\n"
    )
    fp.write(
        "#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey\n"
    )
    fp.write(
        f"#KODIPROP:inputstream.adaptive.license_key={drm_key}\n"
    )


def load_channels():
    with urlopen(JSON_URL, timeout=60) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def is_valid_stream_url(url):
    url = (url or "").strip().lower()

    return (
        url.startswith("http://")
        or url.startswith("https://")
        or url.startswith("rtmp://")
        or url.startswith("rtsp://")
    )


def check_stream(item):

    url = item["url"]

    session = get_session()

    try:

        try:
            r = session.head(
                url,
                allow_redirects=True,
                timeout=(5, 10)
            )

            if r.status_code < 400:
                item["status"] = r.status_code
                return item

        except Exception:
            pass

        r = session.get(
            url,
            stream=True,
            allow_redirects=True,
            timeout=(5, 10)
        )

        if r.status_code < 400:
            item["status"] = r.status_code
            return item

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.SSLError,
        requests.exceptions.RequestException,
    ):
        pass

    return None


def collect_streams(channels):

    jobs = []

    for channel in channels:

        channel_id = str(
            channel.get("name", "unknown")
        )

        logo = channel.get("logo", "")

        streams = channel.get("streams", [])

        if not isinstance(streams, list):
            continue

        for stream in streams:

            if not isinstance(stream, dict):
                continue

            stream_name = stream.get(
                "name",
                channel_id
            )

            url = str(
                stream.get("link", "")
            ).strip()

            if not is_valid_stream_url(url):
                continue

            jobs.append({
                "channel_id": channel_id,
                "logo": logo,
                "stream_name": stream_name,
                "url": url,
                "drm_key": stream.get(
                    "drm_key",
                    ""
                ),
                "drm_scheme": stream.get(
                    "drm_scheme",
                    ""
                )
            })

    return jobs


def main():

    print("Loading channels...")

    channels = load_channels()

    jobs = collect_streams(channels)

    print(
        f"Checking {len(jobs)} streams "
        f"with {MAX_WORKERS} threads..."
    )

    alive = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = {
            executor.submit(
                check_stream,
                item
            ): item
            for item in jobs
        }

        for future in as_completed(futures):

            result = future.result()

            if result:
                alive.append(result)

                print(
                    f"[OK] "
                    f"{result['stream_name']}"
                )

    total_streams = 0
    total_drm = 0

    with open(
        M3U_FILE,
        "w",
        encoding="utf-8"
    ) as m3u, open(
        LOG_FILE,
        "w",
        encoding="utf-8"
    ) as log:

        m3u.write("#EXTM3U\n")

        for item in alive:

            drm_value = normalize_drm_key(
                item["drm_key"]
            )

            m3u.write(
                f'#EXTINF:-1 '
                f'tvg-id="{item["channel_id"]}" '
                f'tvg-name="{item["stream_name"]}" '
                f'tvg-logo="{item["logo"]}" '
                f'group-title="Sports",'
                f'{item["stream_name"]}\n'
            )

            write_kodiprop(
                m3u,
                item["url"],
                item["drm_scheme"],
                item["drm_key"]
            )

            m3u.write(
                item["url"] + "\n"
            )

            log.write(
                f"CHANNEL={item['stream_name']}\n"
                f"URL={item['url']}\n"
                f"HTTP_STATUS={item.get('status', '')}\n"
                f"DRM_SCHEME={item['drm_scheme']}\n"
                f"DRM_KEY={drm_value}\n"
                "----------------------------------------\n"
            )

            total_streams += 1

            if drm_value:
                total_drm += 1

    print()
    print(f"VALID   : {total_streams}")
    print(f"DRM     : {total_drm}")
    print(f"SAVED   : {M3U_FILE}")
    print(f"LOG     : {LOG_FILE}")


if __name__ == "__main__":
    main()
