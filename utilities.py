from constants import (
    INVALID_ARGUMENTS,
    INTERNAL_ERROR,
    error_messages,
    EOL
)
from os import path


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
