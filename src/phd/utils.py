import os
from pathlib import Path

def check_make_dir(path):
    # If folder doesn't exist, then create it.
    check_path = os.path.isdir(path)
    if not check_path:
        os.makedirs(path)
        print("created folder : ", path)

    else:
        print(path, "folder already exists.")