#!/usr/bin/env python
# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $

import optparse
import socket
import sys
import connection
import threading
from constants import *


class Server(object):
    """
    El servidor, que crea y atiende el socket en la dirección y puerto
    especificados donde se reciben nuevas conexiones de clientes.
    """

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT,
                 directory=DEFAULT_DIR):
        print("Serving %s on %s:%s." % (directory, addr, port))
        # FALTA: Crear socket del servidor, configurarlo, asignarlo
        # a una dirección y puerto, etc.
        self.directory = directory
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((addr, port))

        # Escuchar una conexión a la vez
        self.socket.listen(1)
        print(f"Socket creado y enlazado a {addr}:{port}.")
        print("Esperando conexiones...")

    def serve(self):
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """
        while True:
            try:
                # Aceptar conexión
                client_socket, client_address = self.socket.accept()
                print(f"Conexión aceptada de {client_address}")

                conn = connection.Connection(client_socket, self.directory)
                thread = threading.Thread(target=conn.handle)
                thread.start()
 
            except (socket.error, KeyboardInterrupt) as e:
                print(f"Error o interrupción: {e}")
                break


def main():
    """Parsea los argumentos y lanza el server"""

    parser = optparse.OptionParser()
    parser.add_option(
        "-p", "--port",
        help="Número de puerto TCP donde escuchar", default=DEFAULT_PORT)
    parser.add_option(
        "-a", "--address",
        help="Dirección donde escuchar", default=DEFAULT_ADDR)
    parser.add_option(
        "-d", "--datadir",
        help="Directorio compartido", default=DEFAULT_DIR)

    options, args = parser.parse_args()
    if len(args) > 0:
        parser.print_help()
        sys.exit(1)
    try:
        port = int(options.port)
    except ValueError:
        sys.stderr.write(
            "Numero de puerto invalido: %s\n" % repr(options.port))
        parser.print_help()
        sys.exit(1)

    server = Server(options.address, port, options.datadir)
    server.serve()

    # Para ejecutar una prueba, hay que ejecutar server.py y luego
    # en otra terminal "telnet localhost 19500", notar que server.py 
    # se puede ejecutar en distintos puertos y direcciones (los del ejemplo de arriba
    # son los que estan por defecto si se ejecuta "python3 server.py"), por lo que si se pasa 
    # una de esas flags, hay que usar el mismo puerto y dirección en telnet.

    #por ejemplo: python3 server.py -a 127.0.0.1 -p 8080
    #en la otra terminal: telnet 127.0.0.1 8080

    # la flag de dataDir solo indica a que directorio tiene acceso el cliente que se conecte, 
    # yo estuve probando con el directorio por defecto, ya que no tenemos comandos implementados


if __name__ == '__main__':
    main()
