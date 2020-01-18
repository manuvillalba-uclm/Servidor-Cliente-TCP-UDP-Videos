#!/usr/bin/make -f
# -*- mode:makefile -*-

all:

clean:
	$(RM) -r /tmp/db
	$(RM) -r /tmp/YoutubeDownloaderApp

run: clean
	$(MAKE) app-workspace
	$(MAKE) run-registry-node &
	sleep 2
	$(MAKE) run-downloads-node &
	sleep 2
	$(MAKE) run-orchestrator-node

run-client-download:
ifeq ($(1),)
	@echo "Pruebe con run-client-download 1 = <url>"
else
	python ./client.py --Ice.Config=locator.config "orchestrator" --download "$1"
endif

run-client-transfer:
ifeq ($(1),)
	@echo "Pruebe con run-client-transfer 1 = <nombre.mp3>"
else
	python ./client.py --Ice.Config=locator.config "orchestrator" --transfer "$1"
endif

run-client-list:
	python ./client.py --Ice.Config=locator.config "orchestrator"

run-registry-node: /tmp/db/registry /tmp/db/registry-node/servers 
	icegridnode --Ice.Config=registry-node.config

run-orchestrator-node: /tmp/db/orchestrator-node/servers 
	icegridnode --Ice.Config=orchestrator-node.config

run-downloads-node: /tmp/db/downloads-node/servers 
	icegridnode --Ice.Config=downloads-node.config

app-workspace: /tmp/YoutubeDownloaderApp
	cp trawlnet.ice orchestrator.py downloader_factory.py \
	transfer_factory.py utils.py /tmp/YoutubeDownloaderApp
	icepatch2calc /tmp/YoutubeDownloaderApp

/tmp/%:
	mkdir -p $@
