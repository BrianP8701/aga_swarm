import shutil
from pydantic import validate_arguments

# Function to move a folder on a mac
@validate_arguments
def mac_move_folder(folder_path: str, new_folder_path: str) -> dict:
    try:
        # Move the folder to the new location
        shutil.move(folder_path, new_folder_path)
        return {'status_message': 'Success'}
    except Exception as e:
        # Return failure message and the error
        return {'status_message': 'Failure', 'error_message': str(e)}

# Main section
@validate_arguments
def main(folder_path: str, new_folder_path: str) -> dict:
    return mac_move_folder(folder_path, new_folder_path)