import connection
from constants import *
from os import listdir
from utilities import *

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