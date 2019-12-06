#!/usr/bin/python -u
# -*- coding: utf-8 -*-


import sys
import Ice

Ice.loadSlice('trawlnet.ice')

import TrawlNet


class Orchestrator1(TrawlNet.Orchestrator, Ice.Application):
    n = 0

    def downloadTask(self, message, current=None):
        print("Orchestator {0}: {1}".format(self.n, message))
        sys.stdout.flush()
        self.n += 1


        proxy = Server.communicator().stringToProxy(prx)
        msg = TrawlNet.DownloaderPrx.checkedCast(proxy)
        val = msg.addDownloadTask(message)
        return val


class Server(Ice.Application):

    def run(self, argv):
        broker = self.communicator()
        servant = Orchestrator1()


        adapter = broker.createObjectAdapter("OrchestratorAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("orchestrator"))

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0


prx = sys.argv[1]
server = Server()
sys.exit(server.main(sys.argv))