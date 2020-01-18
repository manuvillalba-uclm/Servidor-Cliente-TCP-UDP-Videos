#!/usr/bin/python
# -*- coding: utf-8 -*-
"""client.py
Creado por Manuel Villalba y Luis Pajarero
Sistemas Distribuidos 2019/2020

Utilizado por el usuario para comunicarse con el servidor, el proxy con el que se
comunica es el grupo de réplica orchestrator, las opciones:

    no opción: Solicita la lista completa de descargas.

    --download <url>: Solicitar una descarga de una url válida.

    --transfer <nombre.mp3>: Solicita una transfererencia del archivo nombre.mp3
"""

import binascii
import sys
import getopt
import os
import Ice



Ice.loadSlice('trawlnet.ice')
# desctivamos porque import TrawlNet funciona correctamente pero sólo después de
# hacer Ice.loadSlice('trawlnet.ice')

# pylint: disable=E0401,C0413
import TrawlNet

APP_DIRECTORY = './'
DOWNLOADS_DIRECTORY = os.path.join(APP_DIRECTORY, 'downloads')


class Client(Ice.Application):
    """clase Client
    Creado por Manuel Villalba y Luis Pajarero
    Sistemas Distribuidos 2019/2020

    Clase principal de cliente.

    Contiene run y transfer_request, este último aportado por los profesores de la asignatura.
    """
    filelist = []
    orchestrator = None

    def transfer_request(self, file_name):
        """clase Client
        Creado por Manuel Villalba y Luis Pajarero
        Sistemas Distribuidos 2019/2020

        transfer_request(self, file_name):

        Argumentos:
            file_name: nombre del archivo recibido por argumentos cuando la opción --transfer
                está activa.
        """
        # Nombres aportados por los profesores
        # pylint: disable=C0103
        remote_EOF = False
        # pylint: disable=C0103
        BLOCK_SIZE = 1024
        transfer = None

        try:
            transfer = self.orchestrator.getFile(file_name)
        except TrawlNet.TransferError as e:
            print(e.reason)
            return 1
        except Ice.Exception as e:
            print("El archivo no existe!, "
                  "a continuación se mostrará la lista de archivos descargados actualmente:")
            self.filelist = self.orchestrator.getFileList()
            print(self.filelist)
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
    #Le tengo que pasar los argumentos de alguna forma..
    # pylint: disable=W0221
    def run(self, argv):
        #Compruebo el proxy
        proxy = self.communicator().stringToProxy(argv[1])

        self.orchestrator = TrawlNet.OrchestratorPrx.checkedCast(proxy)
        if not self.orchestrator:
            raise RuntimeError('Invalid proxy')


        #Compruebo las opciones
        try:
            #args sí se usa pero como arg
            # pylint: disable=W0612
            opts, args = getopt.getopt(sys.argv[2:], "", ["download=", "transfer="])
        except getopt.GetoptError as err:
            print(err)
            sys.exit(2)

        if len(opts) == 0:
            self.filelist = self.orchestrator.getFileList()
            print(self.filelist)
        for opt, arg in opts:
            if opt == "--download":
                print("DOWNLOAD")
                sys.stdout.flush()
                url = arg
                try:
                    val = self.orchestrator.downloadTask(url)
                    if val.name == "REPETIDO" and val.hash == "":
                        print("Este archivo ya está descargado en el Servidor")
                        print("A continuación se mostrará la lista de archivos "
                              "descargados actualmente:")
                        self.filelist = self.orchestrator.getFileList()
                        print(self.filelist)
                        sys.stdout.flush()
                    else:
                        print(val)
                        sys.stdout.flush()

                except Ice.Exception as error:
                    print(error)
                    print("URL incompleta o red no disponible.")
                    return 0



            elif opt == "--transfer":
                print("TRANSFER")
                sys.stdout.flush()
                archivo = arg
                self.transfer_request(archivo)

        return 0


sys.exit(Client().main(sys.argv))
