import connection
from constants import *

def quit_handler(cnn, command_parts):
    """
    Maneja el comando quit.
    """
    if len(command_parts) > 1:
        cnn.socket.send(
        f"{INVALID_ARGUMENTS} {error_messages[INVALID_ARGUMENTS]}\r\n".encode()
        )
        return
    cnn.socket.send(f"{CODE_OK} Bye.\r\n".encode())
    cnn.connected = False