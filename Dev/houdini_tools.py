from os import mkdir
from pathlib import Path

import hou

from core import (parse_scene_name, build_scene_name, get_next_version,
                  is_valid_name_part, build_scene_folder)


def version_up():
    """Save the current scene as a new version."""
    scene_name = hou.hipFile.basename()

    split_name = parse_scene_name(scene_name)
    if split_name is None:
        default_shot = ""
        default_task = ""
    else:
        default_shot, default_task, _ = split_name
    print(default_shot, default_task)
    return

    button, value = hou.ui.readMultiInput(-1, split_name)
    if button != 0:
        return None

    if is_valid_name_part(shot) or is_valid_name_part(task) is None:
        hou.ui.diplayMessage("La task est invalide")
        return None

    path = JOB/f"{build_scene_folder(shot, task)}"
    return path

    version = get_next_version(shot, task)
    return version

    file_name= build_scene_folder(shot, task)
    return file_name

    mkdir(path)
    # 8. créer le dossier, puis sauvegarder le chemin complet