#!/usr/bin/env python3

import json
from urllib.request import urlopen

JSON_URL = "https://raw.githubusercontent.com/darkbyteprojects/iptv_png/main/provider_1/sports_channels.json"

M3U_FILE = "stv10.m3u"
LOG_FILE = "stv10.log"


def normalize_drm_key(drm_key):
    """
    Convert:
    {
      "keys":[{"kid":"xxx","k":"yyy"}]
    }

    to:

    xxx:yyy
    """

    if not drm_key:
        return ""

    if isinstance(drm_key, str):

        drm_key = drm_key.strip()

        if ":" in drm_key and not drm_key.startswith("{"):
            return drm_key

        try:
            obj = json.loads(drm_key)

            if "keys" in obj and obj["keys"\]:
                item = obj["keys"][0]

                kid = item.get("kid", "")
                key = item.get("k", "")

                if kid and key:
                    return f"{kid}:{key}"

        except Exception:
            pass

    elif isinstance(drm_key, dict):

        if "keys" in drm_key and drm_key["keys"\]:

            item = drm_key["keys"][0]

            kid = item.get("kid", "")
            key = item.get("k", "")

            if kid and key:
                return f"{kid}:{key}"

    return ""


def write_kodi_props(fp, url, drm_scheme, drm_key):

    drm_key = normalize_drm_key(drm_key)

    if not drm_key:
        return

    drm_scheme = (drm_scheme or "").lower()

    if drm_scheme != "clearkey":
        return

    manifest = "hls"

    if ".mpd" in url.lower():
        manifest = "mpd"

    fp.write(
        "#KODIPROP:inputstream=inputstream.adaptive\n"
    )

    fp.write(
        f"#KODIPROP:inputstream.adaptive.manifest_type={manifest}\n"
    )

    fp.write(
        "#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey\n"
    )

    fp.write(
        f"#KODIPROP:inputstream.adaptive.license_key={drm_key}\n"
    )


def load_json():

    with urlopen(JSON_URL, timeout=60) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def main():

    channels = load_json()

    total = 0
    drm_count = 0

    with open(M3U_FILE, "w", encoding="utf-8") as m3u, \
         open(LOG_FILE, "w", encoding="utf-8") as log:

        m3u.write("#EXTM3U\n")

        for channel in channels:

            channel_id = channel.get("name", "unknown")
            logo = channel.get("logo", "")

            streams = channel.get("streams", [])

            for stream in streams:

                name = stream.get(
                    "name",
                    channel_id
                )

                url = stream.get(
                    "link",
                    ""
                ).strip()

                drm_key = stream.get(
                    "drm_key",
                    ""
                )

                drm_scheme = stream.get(
                    "drm_scheme",
                    ""
                )

                if not url:
                    continue

                m3u.write(
                    f'#EXTINF:-1 tvg-id="{channel_id}" '
                    f'tvg-name="{name}" '
                    f'tvg-logo="{logo}" '
                    f'group-title="Sports",{name}\n'
                )

                write_kodi_props(
                    m3u,
                    url,
                    drm_scheme,
                    drm_key
                )

                m3u.write(url + "\n")

                log.write(
                    f"CHANNEL={name}\n"
                    f"URL={url}\n"
                    f"DRM_SCHEME={drm_scheme}\n"
                    f"DRM_KEY={normalize_drm_key(drm_key)}\n"
                    "----------------------------------\n"
                )

                total += 1

                if normalize_drm_key(drm_key):
                    drm_count += 1

    print(f"Streams  : {total}")
    print(f"DRM      : {drm_count}")
    print(f"M3U File : {M3U_FILE}")
    print(f"LOG File : {LOG_FILE}")


if __name__ == "__main__":
    main()
