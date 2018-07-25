## New Yorker Fiction Podcast data

This repository contains code to harvest a full list of New Yorker Fiction Podcast episodes from the `newyorker.com` and match the readers and writers to Wikidata.

Python scripts to harvest data are in the `scripts` directory. The resulting data is stored in the `data` directory as csvs.

The data can be queried using [Datasette](https://github.com/simonw/datasette) at: [nyperfp-demo-datasette.now.sh](https://nyerfp-demo-datasette.now.sh/).

This post has more details: [lawlesst.github.io/notebook/nyer-fiction.html](http://lawlesst.github.io/notebook/nyer-fiction.html)

This code was written and run with Python 3.

## Updating
New episodes can be harvested and an updated Datasette can be published with the following steps:

* `python scripts/harvest.py > data/episodes.csv`
* `python scripts/wd_details.py data/episodes.csv data/people.csv`
* `csvs-to-sqlite -s'|' data/episodes.csv data/people.csv nyer-fiction-podcast.db`
* `datasette publish -m metadata.json now nyer-fiction-podcast.db`
* Alias this now instance id to a domain name, e.g: `now alias datasette-xxx.now.sh nyerfp-demo-datasette`
