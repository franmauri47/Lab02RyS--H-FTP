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
        data = self.socket.recv(BUFFER_LIMIT).decode("ascii")
        self.buffer += data


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
            if not self.buffer:
                raise ConnectionResetError("Conexión terminada repentinamente "
                                            "por el cliente.")
        return ""

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        while True:
            # Si no esta conectado, salimos del loop
            if not self.connected:
                self.socket.close()
                break

            try:
                # Leemos el mensaje entrante
                error = False
                command = self.read_line()
            except (ConnectionResetError, OSError) as e:
                print(f"Error de red: {e}")
                error = True
            except UnicodeDecodeError as e:
                self.socket.send(
                (f"{BAD_REQUEST} {error_messages[BAD_REQUEST]}:" 
                " El comando contiene caracteres no-ASCII.\r\n").encode())
                error = True
            except Exception as e:
                print(f"Error inesperado: {e}")
                error = True
            finally:
                if error:
                    self.connected = False
                    break

            command_parts = command.split()
            if len(command_parts) == 0:
                self.socket.send((f"{BAD_REQUEST}" 
                                 f" {error_messages[BAD_REQUEST]}:"
                                 " No se pudo parsear el comando\r\n")
                                 .encode())
                continue

            match command_parts[0]:
                case "quit":
                    quit_handler(self, command_parts)
                case "get_file_listing":
                    file_listing_handler(self, command_parts)
                case "get_metadata":
                    get_metadata_handler(self, command_parts)
                case "get_slice":
                    get_slice_handler(self, command_parts)
                case _:
                    self.socket.send(
                        f"{INVALID_COMMAND}" 
                        f" {error_messages[INVALID_COMMAND]}\r\n"
                        .encode()
                    )
