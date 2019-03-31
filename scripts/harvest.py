import csv
import sys
from datetime import datetime
import json
import re
import urllib

import requests
import requests_cache

from bs4 import BeautifulSoup

try:
    cache = requests_cache.install_cache('data/nyer')
except ImportError:
    eprint("Continuing without requests cache")

pages = 15

wd = "https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search="

# For some episodes, we need to manually clean up names or resolve to wikidata.
known = {
    'head-cold': {"writer": "Harold Brodkey", "reader": "jeffrey eugenides", "reader_wikidata": "Q357108"},
    'junot-diaz-reads-how-to-date-a-brown-girl-black-girl-white-girl-or-halfie': {'writer': "Edwidge Danticat"},
    'nathan-englander-reads-john-cheevers-the-enormous-radio': {'writer': "John Cheever"},
    'george-saunders-reads-love-grace-paley-and-the-wretched-seventies-barry-hannah': {'writer': "Barry Hannah"},
    'e-l-doctorow-reads-john-ohara': {"writer_wikidata": "Q548345"},
    'marisa-silver-reads-peter-taylor': {"writer_wikidata": "Q979076"},
    'karl-ove-knausgaard-reads-v-s-naipaul': {"reader_wikidata" :'Q609317'},
    'joseph-oneill-reads-muriel-spark': {"reader_wikidata": "Q151708"},
    'dave-eggers-reads-sam-shepard': {"writer_wikidata": "Q294583"}
    #'': {"writer_wikidata": ""}
}

skip = ['fiction-podcast-bonus-david-sedaris-reads-miranda-july']


def eprint(*args, **kwargs):
    #https://stackoverflow.com/a/14981125/758157
    print(*args, file=sys.stderr, **kwargs)


def get_wikidata(person):
    #print(pod['title'])
    eprint(person)
    url = wd + urllib.parse.quote_plus(person.strip('.'))
    #eprint(url)
    rsp = requests.get(url)
    meta = rsp.json()
    found = meta['search']
    if len(found) == 1:
        return found[0]["id"]
    else:
        for result in found:
            desc = result.get("description")
            if desc is None:
                continue
            for phrase in ("writer", "novelist", "author"):
                if phrase.lower() in desc.lower():
                    return result["id"]
                else:
                    #eprint("*** " + desc)
                    pass


def get_reader_writer(title):
    chunked = re.split("reads|discusses", title.lower())
    reader = chunked[0].strip()
    try:
        if "by" in chunked[1]:
            writer = chunked[1].split("by")[1].strip()
        else:
            writer = chunked[1].strip()
    except IndexError:
        writer = "unknown"
    if known.get(reader) is not None:
        reader = known.get(reader)
    if known.get(writer) is not None:
        writer = known.get(writer)
    return reader.title(), writer.title()


def get_page(num):
    base = "https://www.newyorker.com/podcast/fiction/page/"
    rsp = requests.get(base + str(num))
    soup = BeautifulSoup(rsp.text, "html.parser")
    out = []
    for pod in soup.find_all("li", class_="River__riverItem___3huWr"):
        meta = {}
        partial = pod.find("a", class_="Link__link___3dWao").attrs["href"]
        pid = partial.split("/")[-1]
        if pid in skip:
            continue
        meta['id'] = pid
        meta["url"] = "https://www.newyorker.com" + partial
        meta['title'] = pod.find("h4").text
        try:
            summary = pod.find("h5", class_="River__dek___CayIg").text
        except AttributeError:
            summary = None
        meta['summary'] = summary

        meta['date_published'] = datetime.strptime(
                pod.find("h6", class_="River__publishDate___1fSSK").text,
                "%B %d, %Y"
                ).date()
        # Manually add some details.
        meta.update(known.get(pid, {}))
        reader, writer = get_reader_writer(meta['title'])
        if meta.get('reader') is None:
            meta['reader'] = reader
        if meta.get('writer') is None:
            meta['writer'] = writer
        if meta.get('reader_wikidata') is None:
            meta['reader_wikidata'] = get_wikidata(meta["reader"])
        if meta.get('writer_wikidata') is None:
            meta['writer_wikidata'] = get_wikidata(meta["writer"])
        out.append(meta)

    return out


if __name__ == "__main__":
    out = []
    for x in range(1, pages + 1):
        eprint("Getting page " + str(x))
        out += get_page(x)

    header = [k for k in out[0].keys()]
    writer = csv.DictWriter(sys.stdout, fieldnames=header, delimiter="|")
    writer.writeheader()
    for item in out:
        writer.writerow(item)
