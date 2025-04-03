import connection
from constants import *
from os import path, listdir

def quit_handler(cnn, command_parts):
    """
    Maneja el comando quit.
    """
    if not check_argument_count(cnn, command_parts, 1):
        return
    cnn.socket.send(f"{CODE_OK} Bye.\r\n".encode())
    cnn.connected = False


def file_listing_handler(cnn, command_parts):
    """
    Maneja el comando get_file_listing.
    """
    if not check_argument_count(cnn, command_parts, 1):
        return
    
    if not check_directory_exists(cnn, cnn.directory):
        return
    
    try:
        files = listdir(cnn.directory)
        response = f"{CODE_OK} {error_messages[CODE_OK]} {EOL}"
        for file in files:
            response += f"{file}{EOL}"
        response += f"{EOL}"
        cnn.socket.send(response.encode())
    except:
        send_response(cnn, INTERNAL_ERROR)
        return

    return


def check_argument_count(cnn, command_parts, expected_count):
    """
    Verifica si el número de argumentos es correcto.
    """
    if len(command_parts) != expected_count:
        send_response(cnn, INVALID_ARGUMENTS)
        return False
    return True


def check_directory_exists(cnn, directory):
    """
    Verifica si el directorio existe.
    """
    if not path.exists(directory):
        send_response(cnn, INTERNAL_ERROR)
        return False
    return True


def send_response(cnn, code):
    """
    Respuesta modularizada.
    """
    cnn.socket.send(
        (f"{code} {error_messages[code]}{EOL}").encode()
        )