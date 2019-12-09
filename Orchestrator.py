#!/usr/bin/python -u
# -*- coding: utf-8 -*-


import sys
import Ice
import IceStorm
Ice.loadSlice('trawlnet.ice')

import TrawlNet


class Orchestrator1(TrawlNet.Orchestrator, TrawlNet.OrchestratorEvent, TrawlNet.UpdateEvent, Ice.Application):
    n = 0

    FileList = []

    def downloadTask(self, message, current=None):
        print("Orchestator {0}: {1}".format(self.n, message))
        sys.stdout.flush()
        self.n += 1
        # comprobar primero que el fichero ya exista
        proxy = Orchestrator.communicator().stringToProxy(prx)
        msg = TrawlNet.DownloaderPrx.checkedCast(proxy)
        val = msg.addDownloadTask(message)
        return val

    def newFile(self,val,current=None):
        print("Me ha llegado por subcripcion {0}, {1}".format(val.name,val.hash))
        self.FileList.append(val)
        print(self.FileList)


    def hello (self, me, current = None):

        print("Hola a todos, soy {}".format(me))

        anunciador = TrawlNet.OrchestratorPrx.checkedCast(me)

        if not anunciador:
            raise RuntimeError('Invalid proxy')

        anunciador.announce(miProxy)

    def announce(self, otro,current = None ):
        print("Encantado, soy {}".format(otro))


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
        global miProxy

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

        topic1.subscribeAndGetPublisher(qos, subscriber)
        print("Waiting UpadteEvents... '{}'".format(subscriber))

        #CANAL ORCHESTRATOR SYNC
        topic_name2 = "OrchestratorSync"
        qos2 = {}
        try:
            topic2 = topic_mgr.retrieve(topic_name2)
        except IceStorm.NoSuchTopic:
            topic2 = topic_mgr.create(topic_name2)

        publisher = topic2.getPublisher()
        sync = TrawlNet.OrchestratorEventPrx.uncheckedCast(publisher)
        anunciador = TrawlNet.OrchestratorPrx.uncheckedCast(publisher)

        miProxy = TrawlNet.OrchestratorPrx.checkedCast(proxy)
        sync.hello(miProxy) #Saludar a los Orchestrator

        #ME SUBSCRIBO DESPUÉS DE ENVIAR MI HELLO PARA QUE NO ME LLEGUE A MI
        topic2.subscribeAndGetPublisher(qos2, subscriber)
        print("Waiting SyncEvents... '{}'".format(subscriber))

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic1.unsubscribe(subscriber)
        topic2.unsubscribe(subscriber)

        return 0


prx = sys.argv[1]


orchestrator = Orchestrator()
sys.exit(orchestrator.main(sys.argv))