#!/usr/bin/python -u
# -*- coding: utf-8 -*-


import sys
import Ice
import IceStorm
Ice.loadSlice('trawlnet.ice')

import TrawlNet


class Orchestrator1(TrawlNet.Orchestrator, TrawlNet.OrchestratorEvent, TrawlNet.UpdateEvent, Ice.Application):

    FileList = []
    prxDownloader = None
    prxTransfer = None
    def downloadTask(self, message, current=None):
        # comprobar primero que el fichero ya exista
        proxy = Orchestrator.communicator().stringToProxy(self.prxDownloader)

        factory = TrawlNet.DownloaderFactoryPrx.checkedCast(proxy)
        downloader = factory.create()
        val = downloader.addDownloadTask(message)

        return val

    def newFile(self,val,current=None):
        if val not in self.FileList:
            print("Me ha llegado por subcripcion {0}, {1}".format(val.name, val.hash))
            self.FileList.append(val)
            print(self.FileList)

    def hello (self, me, current = None):
        print("Hola a todos, soy {}".format(me))
        anunciador = TrawlNet.OrchestratorPrx.checkedCast(me)
        if not anunciador:
            raise RuntimeError('Invalid proxy')

        if not me == miProxy :
            anunciador.announce(miProxy)

        for i in self.FileList:
            events.newFile(i)

    def announce(self, otro,current = None ):
        print("Encantado, soy {}".format(otro))

    def getFileList(self, current = None):
        return self.FileList

    def getFile(self, name, current = None):
        proxy = Orchestrator.communicator().stringToProxy(self.prxTransfer)
        factory = TrawlNet.TransferFactoryPrx.checkedCast(proxy)
        transfer = factory.create(name)
        return transfer


class Orchestrator(Ice.Application):

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            return None

        #print("Using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        global miProxy
        global events

        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            print("Invalid proxy")
            return 2

        broker = self.communicator()
        servant = Orchestrator1()

        adapter = broker.createObjectAdapter("OrchestratorAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("orchestrator"))
        subscriber = adapter.addWithUUID(servant)

        #CANAL UPDATE EVENTS
        topic_name1 = "UpdateEvents"
        qos = {}
        try:
            topic1 = topic_mgr.retrieve(topic_name1)
        except IceStorm.NoSuchTopic:
            topic1 = topic_mgr.create(topic_name1)

        publisher1 = topic1.getPublisher()
        events = TrawlNet.UpdateEventPrx.uncheckedCast(publisher1)
        topic1.subscribeAndGetPublisher(qos, subscriber)
        #print("Waiting UpadteEvents... '{}'".format(subscriber))

        #CANAL ORCHESTRATOR SYNC
        topic_name2 = "OrchestratorSync"
        qos2 = {}
        try:
            topic2 = topic_mgr.retrieve(topic_name2)
        except IceStorm.NoSuchTopic:
            topic2 = topic_mgr.create(topic_name2)

        publisher2 = topic2.getPublisher()
        sync = TrawlNet.OrchestratorEventPrx.uncheckedCast(publisher2)

        miProxy = TrawlNet.OrchestratorPrx.checkedCast(proxy)
        topic2.subscribeAndGetPublisher(qos2, subscriber)
        #print("Waiting SyncEvents... '{}'".format(subscriber))
        sync.hello(miProxy) #Saludar a los Orchestrator

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic1.unsubscribe(subscriber)
        topic2.unsubscribe(subscriber)

        return 0


Orchestrator1.prxDownloader = sys.argv[2]
Orchestrator1.prxTransfer = sys.argv[3]

orchestrator = Orchestrator()
sys.exit(orchestrator.main(sys.argv))