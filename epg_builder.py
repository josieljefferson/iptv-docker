import gzip
import shutil
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import re

# =============================
# CONFIG
# =============================

EPG_SOURCES = [
    {"url": "https://m3u4u.com/epg/jq2zy9epr3bwxmgwyxr5", "priority": 1},
    {"url": "https://m3u4u.com/epg/3wk1y24kx7uzdevxygz7", "priority": 2},
    {"url": "https://m3u4u.com/epg/782dyqdrqkh1xegen4zp", "priority": 3},
    {"url": "https://www.open-epg.com/files/brazil1.xml.gz", "priority": 4},
    {"url": "https://www.open-epg.com/files/brazil2.xml.gz", "priority": 5},
    {"url": "https://www.open-epg.com/files/brazil3.xml.gz", "priority": 6},
    {"url": "https://www.open-epg.com/files/brazil4.xml.gz", "priority": 7},
    {"url": "https://www.open-epg.com/files/portugal1.xml.gz", "priority": 8},
    {"url": "https://www.open-epg.com/files/portugal2.xml.gz", "priority": 9},
    {"url": "https://epgshare01.online/epgshare01/epg_ripper_BR1.xml.gz", "priority": 10},
    {"url": "https://epgshare01.online/epgshare01/epg_ripper_PT1.xml.gz", "priority": 11}
]

OUTPUT = Path("epg.xml")
TMP = Path("tmp_epg")
TMP.mkdir(exist_ok=True)

# =============================
# CANAIS USADOS
# =============================

USED_CHANNELS = {
    "TVAntena10.br": "ANTENA 10 HD",
    "Cultura.br": "TV CULTURA",
    "tvassembleia": "TV ASSEMBLEIA PI",
    "tv_cancao_nova": "TV CANÇÃO NOVA"
}

def norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())

USED_NORM = {norm(v): k for k, v in USED_CHANNELS.items()}

# =============================
# MERGE
# =============================

root = ET.Element("tv")
added_channels = set()
added_programs = set()

for src in sorted(EPG_SOURCES, key=lambda x: x["priority"]):
    print("⬇️", src["url"])

    gz = TMP / src["url"].split("/")[-1]
    xml = gz.with_suffix("")

    r = requests.get(src["url"], timeout=60)
    gz.write_bytes(r.content)

    with gzip.open(gz, "rb") as f_in, open(xml, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    for _, elem in ET.iterparse(xml, events=("end",)):
        if elem.tag == "channel":
            cid = elem.attrib.get("id")
            cname = elem.findtext("display-name", "")
            match = cid if cid in USED_CHANNELS else USED_NORM.get(norm(cname))

            if match and match not in added_channels:
                elem.attrib["id"] = match
                root.append(elem)
                added_channels.add(match)

            elem.clear()

        elif elem.tag == "programme":
            cid = elem.attrib.get("channel")
            if cid not in added_channels:
                elem.clear()
                continue

            key = f"{cid}-{elem.attrib.get('start')}-{elem.findtext('title','')}"
            if key not in added_programs:
                root.append(elem)
                added_programs.add(key)

            elem.clear()

    if len(added_channels) == len(USED_CHANNELS):
        break

ET.ElementTree(root).write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True
)

print("⚡ epg.xml gerado com sucesso")