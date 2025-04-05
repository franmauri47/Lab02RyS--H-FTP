from constants import (
    CODE_OK,
    EOL,
    INTERNAL_ERROR,
    FILE_NOT_FOUND,
    BAD_OFFSET,
    INVALID_ARGUMENTS,
    error_messages
)
from utilities import (
    check_argument_count,
    check_directory_exists,
    send_response
)
from base64 import b64encode
from os import listdir, stat
from os.path import join, exists, getsize


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
        response = f"{CODE_OK} {error_messages[CODE_OK]}{EOL}"
        for file in files:
            response += f"{file}{EOL}"
        response += f"{EOL}"
        cnn.socket.send(response.encode())
    except Exception as e:
        print(f"Error al listar archivos: {e}")
        send_response(cnn, INTERNAL_ERROR)
        return

    return


def get_metadata_handler(cnn, command_parts):
    """
    Maneja el comando get_metadata.
    """
    if not check_argument_count(cnn, command_parts, 2):
        return

    filename = command_parts[1]
    filepath = join(cnn.directory, filename)

    if not exists(filepath):
        send_response(cnn, FILE_NOT_FOUND)
        return

    try:
        file_size = stat(filepath).st_size
        response = f"{CODE_OK} {error_messages[CODE_OK]} {EOL}"
        response += f"{file_size}{EOL}"
        cnn.socket.send(response.encode())
    except Exception as e:
        print(f"Error al obtener metadatos del archivo: {e}")
        send_response(cnn, INTERNAL_ERROR)


def get_slice_handler(cnn, command_parts):
    """
    Maneja el comando get_slice.
    """
    if not check_argument_count(cnn, command_parts, 4):
        return

    filename, offset_str = command_parts[1], command_parts[2]
    size_str = command_parts[3]

    try:
        offset = int(offset_str)
        size = int(size_str)
        if offset < 0 or size < 0:
            send_response(cnn, INVALID_ARGUMENTS)
            return
    except ValueError:
        send_response(cnn, INVALID_ARGUMENTS)
        return

    filepath = join(cnn.directory, filename)

    if not exists(filepath):
        send_response(cnn, FILE_NOT_FOUND)
        return

    file_size = getsize(filepath)

    if offset + size > file_size:
        send_response(cnn, BAD_OFFSET)
        return

    try:
        with open(filepath, 'rb') as f:
            f.seek(offset)
            chunk = f.read(size)
            encoded_chunk = b64encode(chunk).decode("ascii")

        response = f"{CODE_OK} {error_messages[CODE_OK]} {EOL}"
        response += f"{encoded_chunk} {EOL}"
        cnn.socket.send(response.encode())
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        send_response(cnn, INTERNAL_ERROR)
