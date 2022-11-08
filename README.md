## New Yorker Fiction Podcast data

This repository contains Python 3 code to harvest a full list of New Yorker Fiction Podcast episodes from the `newyorker.com` and match the readers and writers to Wikidata.

This post has more details: [lawlesst.github.io/notebook/nyer-fiction.html](http://lawlesst.github.io/notebook/nyer-fiction.html)

To update the data from the New Yorker website and Wikidata:

`$ make get_data`

To query locally with [Datasette](https://github.com/simonw/datasette):

`$ make serve_datasette`
