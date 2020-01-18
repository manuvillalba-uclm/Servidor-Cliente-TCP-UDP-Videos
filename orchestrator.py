#!/usr/bin/python -u
# -*- coding: utf-8 -*-


import sys
from time import sleep

import Ice
import IceStorm
import random
Ice.loadSlice('trawlnet.ice')

import TrawlNet


class Orchestrator1(TrawlNet.Orchestrator, TrawlNet.OrchestratorEvent, TrawlNet.UpdateEvent, Ice.Application):

    FileList = []
    prxDownloader = None
    prxTransfer = None
    miProxy = None
    events = None

    def downloadTask(self, message, current=None):
        proxy = self.prxDownloader
        print("Me ha llegado una tarea de descarga!")
        sys.stdout.flush()
        #Con url_id podemos comprobar los que están en la lista antes de meterlo
        url_id = message[-11:]
        repetido = False
        for i in self.FileList:
            if i.name[:11] == url_id:
                repetido = True

        if not repetido:
            factory = TrawlNet.DownloaderFactoryPrx.checkedCast(proxy)
            downloader = factory.create()
            val = downloader.addDownloadTask(message)
            downloader.destroy()
        else:
            val = TrawlNet.FileInfo()
            val.name = "REPETIDO"
            val.hash = ""

        return val

    def newFile(self,val,current=None):
        if val not in self.FileList:
            print("Me ha llegado por subcripcion {0}, {1}".format(val.name, val.hash))
            sys.stdout.flush()
            self.FileList.append(val)
            print(self.FileList)
            sys.stdout.flush()

    def hello (self, me, current = None):
        print("Hola a todos, soy {}".format(me))
        sys.stdout.flush()
        anunciador = TrawlNet.OrchestratorPrx.checkedCast(me)
        if not anunciador:
            raise RuntimeError('Invalid proxy')

        if not me == self.miProxy:
            anunciador.announce(self.miProxy)
            sys.stdout.flush()

        for i in self.FileList:
            self.events.newFile(i)

    def announce(self, otro,current = None ):
        print("Encantado, soy {}".format(otro))
        sys.stdout.flush()

    def getFileList(self, current = None):
        return self.FileList

    def getFile(self, name, current = None):
        factory = TrawlNet.TransferFactoryPrx.checkedCast(self.prxTransfer)
        transfer = factory.create(name)
        return transfer


class Orchestrator(Ice.Application):

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            sys.stdout.flush()
            return None

        #print("Using IceStorm in: '%s'" % key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        sleep(random.uniform(0, 10))
        #Conexión con el Factory Downloader
        Orchestrator1.prxDownloader = self.communicator().stringToProxy("downloaderFactory@DownloaderFactory.DownloaderAdapter")
        Orchestrator1.prxTransfer = self.communicator().stringToProxy("transferFactory@TransferFactory.TransferAdapter")
        #IceStorm
        topic_manager = self.communicator().stringToProxy("YoutubeDownloaderApp.IceStorm/TopicManager")
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_manager)
        if not topic_mgr:
            print("Invalid proxy")
            return 2

        broker = self.communicator()


        adapter = broker.createObjectAdapter("OrchestratorAdapter")


        properties = broker.getProperties()
        servant = Orchestrator1(properties.getProperty('Ice.ProgramName'))
        subscriber = adapter.addWithUUID(servant)
        direct_subscriber = adapter.createDirectProxy(subscriber.ice_getIdentity())

        id_ = properties.getProperty('Identity')
        indirect_proxy = adapter.add(servant, broker.stringToIdentity(id_))

        #proxy = adapter.add(servant, broker.stringToIdentity("orchestrator"))

        #indirect_proxy = adapter.add(servant, broker.stringToIdentity("orchestrator"))

        #indirect_proxy = adapter.addWithUUID(servant)
        identidad = indirect_proxy.ice_getIdentity()
        proxy = adapter.createDirectProxy(identidad)



        #CANAL UPDATE EVENTS
        topic_name1 = "UpdateEvents"
        qos = {}
        try:
            topic1 = topic_mgr.retrieve(topic_name1)
        except IceStorm.NoSuchTopic:
            topic1 = topic_mgr.create(topic_name1)

        publisher1 = topic1.getPublisher()
        Orchestrator1.events = TrawlNet.UpdateEventPrx.uncheckedCast(publisher1)
        topic1.subscribeAndGetPublisher(qos, direct_subscriber)


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

        Orchestrator1.miProxy = TrawlNet.OrchestratorPrx.checkedCast(proxy)
        topic2.subscribeAndGetPublisher(qos2, direct_subscriber)

        #print("Waiting SyncEvents... '{}'".format(subscriber))


        sync.hello(Orchestrator1.miProxy) #Saludar a los otros Orchestrator
        print(indirect_proxy)
        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic1.unsubscribe(direct_subscriber)
        topic2.unsubscribe(direct_subscriber)

        return 0


#Orchestrator1.prxDownloader = sys.argv[2]
#Orchestrator1.prxTransfer = sys.argv[3]

orchestrator = Orchestrator()
sys.exit(orchestrator.main(sys.argv))