from flask import Flask, Response, send_file
from flask import Response
import json
import os
import subprocess
from pathlib import Path

app = Flask(__name__)

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080")
CHANNELS = json.load(open("channels.json", encoding="utf-8"))

@app.route("/playlist.m3u")
def playlist():
    lines = ['#EXTM3U url-tvg="https://m3u4u.com/epg/jq2zy9epr3bwxmgwyxr5, https://m3u4u.com/epg/3wk1y24kx7uzdevxygz7, https://m3u4u.com/epg/782dyqdrqkh1xegen4zp, https://www.open-epg.com/files/brazil1.xml.gz, https://www.open-epg.com/files/brazil2.xml.gz, https://www.open-epg.com/files/brazil3.xml.gz, https://www.open-epg.com/files/brazil4.xml.gz, https://www.open-epg.com/files/portugal1.xml.gz, https://www.open-epg.com/files/portugal2.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_BR1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PT1.xml.gz"']
    for c in CHANNELS:
        lines.append(
            f'#EXTINF:-1 tvg-id="{c["id"]}" tvg-name="{c["name"]}" '
            f'tvg-logo="{c["logo"]}",{c["name"]}'
        )
        lines.append(c["url"])
    return Response("\n".join(lines), mimetype="audio/x-mpegurl")

@app.route("/epg.xml")
def epg():
    if not Path("epg.xml").exists():
        subprocess.call(["python", "epg_builder.py"])
    return send_file("epg.xml", mimetype="application/xml")

@app.route("/")
def home():
    return {
        "playlist": f"{BASE_URL}/playlist.m3u",
        "epg": f"{BASE_URL}/epg.xml"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)