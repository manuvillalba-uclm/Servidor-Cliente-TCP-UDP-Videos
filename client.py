#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import sys
import Ice
import getopt
import os

Ice.loadSlice('trawlnet.ice')
import TrawlNet

APP_DIRECTORY = './'
DOWNLOADS_DIRECTORY = os.path.join(APP_DIRECTORY, 'downloads')


class Client(Ice.Application):

    FileList = []
    orchestrator = None

    def transfer_request(self, file_name):
        remote_EOF = False
        BLOCK_SIZE = 1024
        transfer = None

        try:
            transfer = self.orchestrator.getFile(file_name)
        except TrawlNet.TransferError as e:
            print(e.reason)
            return 1
        except Exception as e:
            print("El archivo no existe!, a continuación se mostrará la lista de archivos descargados actualmente:")
            self.FileList = self.orchestrator.getFileList()
            print(self.FileList)
            sys.stdout.flush()
            return 1


        with open(os.path.join(DOWNLOADS_DIRECTORY, file_name), 'wb') as file_:
            remote_EOF = False
            while not remote_EOF:
                data = transfer.recv(BLOCK_SIZE)
                if len(data) > 1:
                    data = data[1:]
                data = binascii.a2b_base64(data)
                remote_EOF = len(data) < BLOCK_SIZE
                if data:
                    file_.write(data)
            transfer.close()

        transfer.destroy()
        print('Transfer finished!')

    def run(self, argv):
        #Compruebo el proxy
        proxy = self.communicator().stringToProxy(argv[1])

        self.orchestrator = TrawlNet.OrchestratorPrx.checkedCast(proxy)
        if not self.orchestrator:
            raise RuntimeError('Invalid proxy')


        #Compruebo las opciones
        try:
            opts, args = getopt.getopt(sys.argv[2:], "", ["download=", "transfer="])
        except getopt.GetoptError as err:
            print(err)
            sys.exit(2)

        if len(opts) == 0:
            self.FileList = self.orchestrator.getFileList()
            print(self.FileList)
        for opt, arg in opts:
            if opt == "--download":
                print("DOWNLOAD")
                sys.stdout.flush()
                url = arg
                val = self.orchestrator.downloadTask(url)
                if val.name == "REPETIDO" and val.hash == "":
                    print("Este archivo ya está descargado en el Servidor")
                    print("A continuación se mostrará la lista de archivos descargados actualmente:")
                    self.FileList = self.orchestrator.getFileList()
                    print(self.FileList)
                    sys.stdout.flush()
                else:
                    print(val)
                    sys.stdout.flush()

            elif opt == "--transfer":
                print("TRANSFER")
                sys.stdout.flush()
                archivo = arg
                self.transfer_request(archivo)

        return 0


sys.exit(Client().main(sys.argv))