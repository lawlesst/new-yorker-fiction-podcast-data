"""
Fetch various details from Wikidata via SPARQL.
"""


import csv
import sys

from SPARQLWrapper import JSON, SPARQLWrapper

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")


def eprint(*args, **kwargs):
    # https://stackoverflow.com/a/14981125/758157
    print(*args, file=sys.stderr, **kwargs)


rq = """
PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

 select distinct
   ?wid
   ?person
   ?personLabel
   ?photo
   ?genderLabel
   ?citizenshipLabel
   ?sitelink
   ?lccn
   ?description
   ?birth
   ?pPrize
WHERE {
  ?person schema:description ?description filter (lang(?description) = "en") .
  OPTIONAL {?person wdt:P21 ?gender}
  OPTIONAL {?person wdt:P27 ?citizenship }
  OPTIONAL {?person wdt:P18 ?photo }
  OPTIONAL {?person wdt:P569 ?birth  }
  OPTIONAL {?person wdt:P244 ?lccn }
  BIND( EXISTS {?person wdt:P166 wd:Q833633} as ?pPrize )
  OPTIONAL {
    ?sitelink schema:about ?person .
    ?sitelink schema:inLanguage "en" .
    ?sitelink schema:isPartOf <https://en.wikipedia.org/>
  }
  SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en" .
  }
  BIND(STRAFTER(str(?person), "http://www.wikidata.org/entity/") as ?wid)
  VALUES ?person { --ids-- }
}"""


def gv(row, _key):
    rsp = row.get(_key)
    if rsp is not None:
        return rsp["value"]


if __name__ == "__main__":
    wd_ids = []
    with open(sys.argv[1]) as infile:
        for row in csv.DictReader(infile, delimiter="|"):
            for wtype in ["reader_wikidata", "writer_wikidata"]:
                wd_ids.append("wd:{}".format(row[wtype]))
    query = rq.replace("--ids--", " ".join(wd_ids))
    eprint(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    columns = results["head"]["vars"]

    resolved_wids = []
    out = []

    with open(sys.argv[2], "w") as outf:
        writer = csv.DictWriter(outf, delimiter="|", fieldnames=columns)
        writer.writeheader()

        for row in results["results"]["bindings"]:
            if row["wid"] in resolved_wids:
                continue
            d = {}
            for c in columns:
                d[c] = row.get(c, {}).get("value")
            out.append(d)
            resolved_wids.append(row["wid"])
        
        for row in sorted(out, key=lambda x: x["wid"]):
            writer.writerow(row)
            writer.writerow(row)
