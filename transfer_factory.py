#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""transfer_factory.py
Creado por Manuel Villalba y Luis Pajarero
Sistemas Distribuidos 2019/2020

Hace posible la transferencia, consiste en una fábrica que crea transfers, cuando
los usan una vez los eiminan.

"""

import os
import sys
import binascii

import Ice

Ice.loadSlice('trawlnet.ice')
# desctivamos porque import TrawlNet funciona correctamente pero sólo después de
# hacer Ice.loadSlice('trawlnet.ice')

# pylint: disable=E0401,C0413
import TrawlNet


APP_DIRECTORY = './'
DOWNLOADS_DIRECTORY = os.path.join(APP_DIRECTORY, 'downloads')


class TransferI(TrawlNet.Transfer):
    """clase TransferI
    Creado por Manuel Villalba y Luis Pajarero
    Sistemas Distribuidos 2019/2020

    Sirviente creado por la factoría.

    Tiene un método constructor, file_path es el nobre del archivo a transferir junto con su ruta
    """
    def __init__(self, file_path):
        self.file_ = open(file_path, 'rb')

    # Ice me obliga a poner current
    # pylint: disable=W0613
    def recv(self, size, current):
        """metodo recv
        Creado por Manuel Villalba y Luis Pajarero
        Sistemas Distribuidos 2019/2020

        creará la tarea para que el transfer transfiera el audio deforma similar a como se realiza
        el envío de información por medio de sockets en python.
        """
        return str(binascii.b2a_base64(self.file_.read(size), newline=False))

    def close(self, current):
        """metodo close
        Creado por Manuel Villalba y Luis Pajarero
        Sistemas Distribuidos 2019/2020

        cerrará el archivo que se haya transferido, propio del objeto transfer concreto.
        """
        self.file_.close()
    # Ice me obliga a poner current
    # Método dado al alumnado.
    # pylint: disable=W0613,R0201
    def destroy(self, current):
        """metodo destroy
        Creado por Manuel Villalba y Luis Pajarero
        Sistemas Distribuidos 2019/2020

        eliminará al transfer del adaptador y terminará su ejecución
        """
        try:
            current.adapter.remove(current.id)
            print('TRASFER DESTROYED', flush=True)
        # Exception es muy general, pero así se ha dado al alumnado.
        # pylint: disable=W0703
        except Exception as error:
            print(error, flush=True)

    # TransferFactory no tiene más métodos
    # pylint: disable=R0903
class TransferFactoryI(TrawlNet.TransferFactory):
    """clase TransferFactoryI
    Creado por Manuel Villalba y Luis Pajarero
    Sistemas Distribuidos 2019/2020

    Sirviente creado por la run.
    """
    # Ice me obliga a poner current
    # Método dado al alumnado.
    # pylint: disable=W0613, R0201
    def create(self, file_name, current):
        """clase create
        Creado por Manuel Villalba y Luis Pajarero
        Sistemas Distribuidos 2019/2020

        devolverá un objeto transfer ya añadido al adaptador de objetos y
         con el archivo a mandar abierto.
        """
        file_path = os.path.join(DOWNLOADS_DIRECTORY, file_name)
        servant = TransferI(file_path)
        proxy = current.adapter.addWithUUID(servant)
        print(proxy)

        return TrawlNet.TransferPrx.checkedCast(proxy)


class Server(Ice.Application):
    """clase Server
    Creado por Manuel Villalba y Luis Pajarero
    Sistemas Distribuidos 2019/2020

    principal
    """
    def run(self, args):
        # Nombre dado al alumnado.
        # pylint: disable=C0103
        ic = self.communicator()
        properties = ic.getProperties()

        servant = TransferFactoryI()
        adapter = ic.createObjectAdapter('TransferAdapter')
        factory_id = properties.getProperty('TransferFactoryIdentity')
        proxy = adapter.add(servant, ic.stringToIdentity(factory_id))

        print('{}'.format(proxy), flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        return 0


if __name__ == '__main__':
    # Nombre dado al alumnado.
    # pylint: disable=C0103
    app = Server()
    # Nombre dado al alumnado.
    # pylint: disable=C0103
    exit_status = app.main(sys.argv)
    sys.exit(exit_status)
