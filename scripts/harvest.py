import csv
import re
import sys
import urllib
from datetime import datetime, timedelta

import requests
import requests_cache
from bs4 import BeautifulSoup

cache = True


try:
    cache = requests_cache.install_cache("data/nyer", expire_after=timedelta(days=7))
except ImportError:
    print("Continuing without requests cache", file=sys.stderr)

wd = "https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search="

# For some episodes, we need to manually clean up names or resolve to wikidata.
known = {
    "head-cold": {
        "writer": "Harold Brodkey",
        "reader": "jeffrey eugenides",
        "reader_wikidata": "Q357108",
    },
    "junot-diaz-reads-how-to-date-a-brown-girl-black-girl-white-girl-or-halfie": {
        "writer": "Edwidge Danticat"
    },
    "nathan-englander-reads-john-cheevers-the-enormous-radio": {
        "writer": "John Cheever"
    },
    "george-saunders-reads-love-grace-paley-and-the-wretched-seventies-barry-hannah": {
        "writer": "Barry Hannah"
    },
    "e-l-doctorow-reads-john-ohara": {"writer_wikidata": "Q548345"},
    "marisa-silver-reads-peter-taylor": {"writer_wikidata": "Q979076"},
    "karl-ove-knausgaard-reads-v-s-naipaul": {"reader_wikidata": "Q609317"},
    "joseph-oneill-reads-muriel-spark": {"reader_wikidata": "Q151708"},
    "dave-eggers-reads-sam-shepard": {"writer_wikidata": "Q294583"},
}

skip = ["fiction-podcast-bonus-david-sedaris-reads-miranda-july"]


def eprint(*args, **kwargs):
    # https://stackoverflow.com/a/14981125/758157
    print(*args, file=sys.stderr, **kwargs)


def get_wikidata(person):
    """Use the Wikidata entity search to find the
    author's Wikidata ID."""
    eprint(person)
    url = wd + urllib.parse.quote_plus(person.strip("."))
    rsp = requests.get(url)
    meta = rsp.json()
    found = meta["search"]
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
                    # eprint("*** " + desc)
                    pass


def get_reader_writer(title):
    """Helper to parse out the reader and the writer from the
    podcast title."""
    title = title.replace(", Live", "")
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
    """
    Parse the list of episodes from newyorker.com.
    """
    url = f"https://www.newyorker.com/podcast/fiction?page={num}"
    rsp = requests.get(url)
    soup = BeautifulSoup(rsp.text, "html.parser")
    out = []

    pods = soup.find_all("h3")
    for pod in pods:
        meta = {}
        partial = pod.find_previous("a").attrs["href"]
        pid = partial.split("/")[-1]
        if pid in skip:
            continue
        meta["id"] = pid
        meta["url"] = "https://www.newyorker.com" + partial
        meta["title"] = pod.text
        try:
            summary = pod.find_next("div", class_="summary-item__dek").text
        except AttributeError:
            summary = None
        meta["summary"] = summary
        meta["date_published"] = datetime.strptime(
            pod.find_next("time").text,
            "%B %d, %Y",
        ).date()
        # Use the manual tweaks from above.
        meta.update(known.get(pid, {}))
        reader, writer = get_reader_writer(meta["title"])
        if meta.get("reader") is None:
            meta["reader"] = reader
        if meta.get("writer") is None:
            meta["writer"] = writer
        if meta.get("reader_wikidata") is None:
            meta["reader_wikidata"] = get_wikidata(meta["reader"])
        if meta.get("writer_wikidata") is None:
            meta["writer_wikidata"] = get_wikidata(meta["writer"])
        out.append(meta)

    return out


if __name__ == "__main__":
    out = []
    page_num = 1
    episodes = []
    while True:
        eprint(f"Getting page {page_num}.")
        details = get_page(page_num)
        if details == []:
            eprint(f"No data found. Breaking at page {page_num}.")
            break
        if page_num == 1:
            header = [k for k in details[0].keys()]
        for pod in details:
            episodes.append(pod)
        page_num += 1
    
    episodes = sorted(episodes, key=lambda x: x["date_published"], reverse=True)
    writer = csv.DictWriter(
                sys.stdout, fieldnames=header, delimiter="|", lineterminator="\n"
    )
    writer.writeheader()
    for episode in episodes:
        writer.writerow(episode)
    
