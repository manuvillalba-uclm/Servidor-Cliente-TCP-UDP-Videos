#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('trawlnet.ice')
import TrawlNet


class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        url = argv[2]
        msg = TrawlNet.OrchestratorPrx.checkedCast(proxy)

        if not msg:
            raise RuntimeError('Invalid proxy')

        msg.downloadTask(url)

        return 0


sys.exit(Client().main(sys.argv))