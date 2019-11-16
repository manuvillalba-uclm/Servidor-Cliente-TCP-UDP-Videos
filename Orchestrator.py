#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import sys
import Ice

Ice.loadSlice('trawlnet.ice')

import TrawlNet


class downloadTask(TrawlNet.Orchestrator):
    n = 0

    def write(self, message, current=None):
        print("{0}: {1}".format(self.n, message))
        sys.stdout.flush()
        self.n += 1


class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        servant = downloadTask()

        adapter = broker.createObjectAdapter("OrchestratorAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("orchestrator"))

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        printer = Downloader.PrinterPrx.checkedCast(proxy)

        if not printer:
            raise RuntimeError('Invalid proxy')

        printer.downloadTask('Hello World!')

        return 0


server = Server()
sys.exit(server.main(sys.argv))
