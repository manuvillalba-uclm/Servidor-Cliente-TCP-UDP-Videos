#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import sys
import Ice

Ice.loadSlice('trawlnet.ice')

import TrawlNet


class Orchestrator1(TrawlNet.Orchestrator, Ice.Application):
    n = 0

    def downloadTask(self, message, current=None):
        print("{0}: {1}".format(self.n, message))
        sys.stdout.flush()
        self.n += 1
        proxy = Server.communicator().stringToProxy("downloader -t -e 1.1:tcp -h 192.168.1.43 -p 9090 -t 60000")
        msg = TrawlNet.DownloaderPrx.checkedCast(proxy)
        msg.addDownloadTask(message)



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






server = Server()
sys.exit(server.main(sys.argv))
