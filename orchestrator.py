#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""orchestrator.py
Creado por Manuel Villalba y Luis Pajarero
Sistemas Distribuidos 2019/2020

Utilizado para asignar tareas al Downloader, está subscrito a dos canales:
    - OrchestratorSync
    - UpdateEvents

Se encarga de mantener una lista de los ficheros que se han descargado en el servidor.
"""
import sys
from time import sleep
import random
import Ice
import IceStorm
Ice.loadSlice('trawlnet.ice')
# desctivamos porque import TrawlNet funciona correctamente pero sólo después de hacer
# Ice.loadSlice('trawlnet.ice')
# pylint: disable=E0401,C0413, unused-argument
import TrawlNet


class Orchestrator1(TrawlNet.Orchestrator, TrawlNet.OrchestratorEvent,
                    TrawlNet.UpdateEvent, Ice.Application):
    """clase Orchestrator1
        Creado por Manuel Villalba y Luis Pajarero
        Sistemas Distribuidos 2019/2020

        Clase principal de Orchestrator

        Contiene todas las funciones y acciones que realiza el Orchestrator.
        """
    FileList = []
    prxDownloader = None
    prxTransfer = None
    miProxy = None
    events = None

    # Desactivamos que el nombre sea inválido porque nos ha sido proporcionado por los profesores
    # pylint: disable=invalid-name
    def downloadTask(self, message, current=None):
        """método donwloadTask
                Creado por Manuel Villalba y Luis Pajarero
                Sistemas Distribuidos 2019/2020

                Envía una URL al Downloader.
        """
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

    def newFile(self, val, current=None):
        """método newFile
                Creado por Manuel Villalba y Luis Pajarero
                Sistemas Distribuidos 2019/2020

                Método para pasar los archivos a los demás Orchestrator.
        """
        if val not in self.FileList:
            print("Me ha llegado por subcripcion {0}, {1}".format(val.name, val.hash))
            sys.stdout.flush()
            self.FileList.append(val)
            print(self.FileList)
            sys.stdout.flush()

    def hello(self, me, current=None):
        """método hello
               Creado por Manuel Villalba y Luis Pajarero
               Sistemas Distribuidos 2019/2020

               Este método manda su proxy a todos los Orchestrator del canal
               Simula un "Saludo".
        """
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

    # Desactivamos porque en la especificación de la práctica es así
    # pylint: disable=no-self-use
    def announce(self, otro, current=None):
        """método newFile
               Creado por Manuel Villalba y Luis Pajarero
               Sistemas Distribuidos 2019/2020

               Cuando le llega un hello de otro Orchestrator, este método
               le devuelve al que saluda su proxy, para que se conozcan.
       """
        print("Encantado, soy {}".format(otro))
        sys.stdout.flush()

    def getFileList(self, current=None):
        """método newFile
               Creado por Manuel Villalba y Luis Pajarero
               Sistemas Distribuidos 2019/2020

               Método para pasase la lista de archivos descargados
        """
        print ("Me ha llegado una tarea para devolver mi LISTA DE ARCHIVOS")
        return self.FileList

    def getFile(self, name, current=None):
        """método newFile
               Creado por Manuel Villalba y Luis Pajarero
               Sistemas Distribuidos 2019/2020

               Método para pasar el archivo de audio del vídeo.
        """
        print ("Me ha llegado una tarea para hacer una TRANSFER")
        factory = TrawlNet.TransferFactoryPrx.checkedCast(self.prxTransfer)
        transfer = factory.create(name)
        return transfer


# Desactivado porque lo tenemos que usar
# pylint: disable=no-member
class Orchestrator(Ice.Application):
    """Clase Orchestrator
           Creado por Manuel Villalba y Luis Pajarero
           Sistemas Distribuidos 2019/2020

           Clase que ejecuta el Orchestrator, en esta clase se forma la lógica del programa
            - Se subscribe a los dos canales
            - Se realiza el hello

    """
    def get_topic_manager(self):
        """Clase Orchestrator
               Creado por Manuel Villalba y Luis Pajarero
               Sistemas Distribuidos 2019/2020

               Método que obtiene el proxy del topic
        """
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property '{}' not set".format(key))
            sys.stdout.flush()
            return None

        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    #Le tengo que pasar los argumentos de alguna forma y necesitamos bastantes variables
    # en este caso..
    # pylint: disable=W0221, too-many-locals
    def run(self, argv):
        # Debido a fallos con IceGrid al iniciar varios orchestrator a la vez creemos que
        # se producen bloqueos interos, que no ocurren si cada orchestrator se inicia en
        # un tiempo diferente
        sleep(random.uniform(0, 10))
        #Conexión con el Factory Downloader
        Orchestrator1.prxDownloader = self.communicator().stringToProxy(
            "downloaderFactory@DownloaderFactory.DownloaderAdapter")
        Orchestrator1.prxTransfer = self.communicator().stringToProxy(
            "transferFactory@TransferFactory.TransferAdapter")
        #IceStorm
        topic_manager = self.communicator().stringToProxy(
            "YoutubeDownloaderApp.IceStorm/TopicManager")
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

        #SALUDAR
        # Saludar a los otros Orchestrator
        sync.hello(Orchestrator1.miProxy)
        print("Indidect:" + indirect_proxy)
        print("Direct" + proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        topic1.unsubscribe(direct_subscriber)
        topic2.unsubscribe(direct_subscriber)

        return 0


ORCHESTRATOR = Orchestrator()
sys.exit(ORCHESTRATOR.main(sys.argv))
