#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import sys
import Ice

Ice.loadSlice('trawlnet.ice')

import TrawlNet


class addDownloadTask(TrawlNet.Downloader):
    n = 0

    def write(self, message, current=None):
        print("{0}: {1}".format(self.n, message))
        sys.stdout.flush()
        self.n += 1


class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        servant = addDownloadTask()

        adapter = broker.createObjectAdapter("DownloaderAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("downloader"))

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))