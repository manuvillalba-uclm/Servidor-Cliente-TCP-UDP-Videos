#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('trawlnet.ice')
import TrawlNet



class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        url = self.communicator().stringToProxy(argv[2])
        printer = TrawlNet.PrinterPrx.checkedCast(proxy)

        if not printer:
            raise RuntimeError('Invalid proxy')

        printer.write(url)

        return 0


sys.exit(Client().main(sys.argv))