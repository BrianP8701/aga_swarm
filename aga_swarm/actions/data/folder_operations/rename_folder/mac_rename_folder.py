import os
from pydantic import validate_arguments

# Function to rename a folder on a Mac
@validate_arguments
def mac_rename_folder(folder_path: str, new_folder_path: str) -> dict:
    try:
        os.rename(folder_path, new_folder_path)
        return {'status_message': 'Success', 'error_message': ''}
    except Exception as e:
        return {'status_message': 'Failure', 'error_message': str(e)}

# Main section
@validate_arguments
def main(folder_path: str, new_folder_path: str) -> dict:
    return mac_rename_folder(folder_path, new_folder_path)