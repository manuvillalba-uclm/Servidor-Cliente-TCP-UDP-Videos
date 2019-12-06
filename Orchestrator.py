#!/usr/bin/python -u
# -*- coding: utf-8 -*-


import sys
import Ice
import IceStorm
Ice.loadSlice('trawlnet.ice')

import TrawlNet


class Orchestrator1(TrawlNet.Orchestrator, TrawlNet.UpdateEvent, Ice.Application):
    n = 0

    def downloadTask(self, message, current=None):
        print("Orchestator {0}: {1}".format(self.n, message))
        sys.stdout.flush()
        self.n += 1

        proxy = Orchestrator.communicator().stringToProxy(prx)
        msg = TrawlNet.DownloaderPrx.checkedCast(proxy)
        val = msg.addDownloadTask(message)
        return val
    def newFile(self,val,current=None):
        print("Me ha llegado por subcripcion {}".format(val.name))
        print(val.hash)

class Orchestrator(Ice.Application):
    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            return None

        print("Using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print("Invalid proxy")
            return 2


        broker = self.communicator()
        servant = Orchestrator1()


        adapter = broker.createObjectAdapter("OrchestratorAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("orchestrator"))
        subscriber = adapter.addWithUUID(servant)

        topic_name = "UpdateEvents"
        qos = {}
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher(qos, subscriber)
        print("Waiting events... '{}'".format(subscriber))

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic.unsubscribe(subscriber)


        return 0


prx = sys.argv[1]


orchestrator = Orchestrator()
sys.exit(orchestrator.main(sys.argv))