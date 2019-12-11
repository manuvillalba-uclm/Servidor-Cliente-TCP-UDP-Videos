#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('trawlnet.ice')
import TrawlNet


class Client(Ice.Application):
    FileList = []

    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])


        msg = TrawlNet.OrchestratorPrx.checkedCast(proxy)

        if not msg:
            raise RuntimeError('Invalid proxy')
        if not argv[2]=="":
            url = argv[2]
            val = msg.downloadTask(url)
        else:
            self.FileList = msg.getFileList()
            print(self.FileList)

        return 0


sys.exit(Client().main(sys.argv))