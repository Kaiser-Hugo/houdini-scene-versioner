import datetime
import getpass
import hou

from datetime import datetime
from pathlib import Path

from core import (parse_scene_name, build_scene_name, get_next_version,
                  is_valid_name_part, build_scene_folder,write_metadata)

LICENSE_EXTENSIONS = {
    hou.licenseCategoryType.Apprentice: "hipnc",
    hou.licenseCategoryType.ApprenticeHD: "hipnc",
    hou.licenseCategoryType.Commercial: "hip",
    hou.licenseCategoryType.Education: "hipnc",
    hou.licenseCategoryType.Indie: "hiplc",
}

def version_up():
    """Save the current scene as a new version."""
    scene_name = hou.hipFile.basename()
    is_new_scene = hou.hipFile.isNewFile()
    source = None if is_new_scene else scene_name

    split_name = parse_scene_name(scene_name)
    if split_name is None:
        default_shot = ""
        default_task = ""
    else:
        default_shot, default_task, _ = split_name

    result = hou.ui.readMultiInput(
        "Scene Name",
        input_labels=("Shot", "Task", "Commentaire"),
        buttons=("OK", "Annuler"),
        initial_contents=(default_shot, default_task, ""),
        close_choice=1,
        title="Scene Versioner",
    )

    button, values = result
    shot, task, comment = values

    if button != 0:
        return None


    if not is_valid_name_part(shot):
        hou.ui.displayMessage("shot invalid")
        return None

    if not is_valid_name_part(task):
        hou.ui.displayMessage("task invalid")
        return None

    job = hou.getenv("JOB")
    if job is None:
        hou.ui.displayMessage("$JOB is not defined : impossible to save")
        return None
    folder = build_scene_folder(Path(job),shot, task)

    version = get_next_version(folder, shot, task)

    extension = LICENSE_EXTENSIONS.get(hou.licenseCategory(), "hip")
    file_name = build_scene_name(shot, task, version, extension)
    scene_path = folder / file_name

    folder.mkdir(parents=True, exist_ok=True)
    hou.hipFile.save(str(scene_path))

    houdini_range = hou.playbar.frameRange()
    frame_range = [int(houdini_range[0]), int(houdini_range[1])]

    metadata = {
        "shot": shot,
        "task": task,
        "version": version,
        "comment": comment,
        "user": getpass.getuser(),
        "date": datetime.now().isoformat(),
        "houdini_version": hou.applicationVersionString(),
        "frame_range": frame_range,
        "source": source,
    }

    json_path = scene_path.with_suffix(".json")
    write_metadata(json_path,metadata)