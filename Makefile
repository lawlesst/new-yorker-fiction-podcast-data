.DEFAULT_GOAL := hello

episodes := data/episodes.csv
people := data/people.csv
database := data/nyer-fiction-podcast.db

hello:
	@echo "Make file. `cat Makefile` to see commands"


harvest:
	$ poetry run python scripts/harvest.py > $(episodes)

wikidata:
	$ poetry run python scripts/wd_details.py $(episodes) $(people)

refresh_data: harvest wikidata

build_datasette_db:
	$ poetry run csvs-to-sqlite -s'|' $(episodes) $(people) $(database)

get_data: harvest wikidata build_datasette_db

serve_datasette:
	$ poetry run datasette serve $(database)