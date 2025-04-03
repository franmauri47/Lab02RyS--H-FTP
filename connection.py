# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
from base64 import b64encode
from cmd_handlers import *

class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.socket = socket
        self.directory = directory
        self.buffer = ''
        self.connected = True

        pass

    def recv(self):
        data = self.socket.recv(4096).decode("ascii")
        self.buffer += data

        if len(data) == 0:
            self.connected = False


    # Habría que revisar cuestiones como evitar DOS, comandos inválidos, etc.
    def read_line(self):
        """
        Espera datos hasta obtener una línea completa delimitada por el
        terminador del protocolo.

        Devuelve la línea, eliminando el terminador y los espacios en blanco
        al principio y al final.
        """
        while self.connected:
            if EOL in self.buffer:
                response, self.buffer = self.buffer.split(EOL, 1)
                return response.strip()
            self.recv()
        return ""

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        while True:
            # Si no esta conectado, salimos del loop
            if not self.connected:
                break

            try:
                # Leemos el mensaje entrante
                command = self.read_line()

                # print BORRAR DESPUES solo debug BORRAR DESPUES solo debug BORRAR DESPUES solo debug BORRAR DESPUES solo debug
                # print(command)

            except (socket.timeout, ConnectionResetError, OSError) as e:
                print(f"Error de red: {e}")
                break
            except Exception as e:
                print(f"Error inesperado: {e}")
                break

            command_parts = command.split()
            if len(command_parts) == 0:
                self.socket.send((f"{BAD_REQUEST}" 
                                 f" {error_messages[BAD_REQUEST]}:"
                                 " No se pudo parsear el comando\r\n")
                                 .encode())
                break

            match command_parts[0]:
                # Si el comando es "quit", cerramos la conexión
                case "quit":
                    quit_handler(self, command_parts)
                case _:
                    self.socket.send(
                        f"{INVALID_COMMAND}" 
                        f" {error_messages[INVALID_COMMAND]}\r\n"
                        .encode()
                    )
            
        self.socket.close()
