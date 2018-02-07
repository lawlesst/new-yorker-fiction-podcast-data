## New Yorker Fiction Podcast data

This repository contains code to harvest a full list of New Yorker Fiction Podcast episodes from the `newyorker.com` and match the readers and writers to Wikidata.

Python scripts to harvest data are in the `scripts` directory. The resulting data is stored in the `data` directory as csvs.

The data can be queried using [Datasette](https://github.com/simonw/datasette) at: [nyperfp-demo-datasette.now.sh](https://nyerfp-demo-datasette.now.sh/).

This code was written and run with Python 3.
