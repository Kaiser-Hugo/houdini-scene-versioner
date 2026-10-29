from pathlib import Path
import re


def parse_scene_name(scene_name: str) -> tuple[str, str, int] | None:
	"""Split a scene file name into (shot, task, version)."""
	split_name = re.fullmatch(r"([a-z0-9]+)_([a-z0-9]+)_v(\d{3})\.hip", scene_name)

	if split_name is None:
		return None

	shot = split_name.group(1)
	task = split_name.group(2)
	version = int(split_name.group(3))
	return shot, task, version


def build_scene_name(shot: str,task: str,version: int) -> str:
	"""Build scene name from shot, task and version"""
	new_scene_name = f"{shot}_{task}_v{version:03d}.hip"
	return new_scene_name

def get_next_version(folder: Path, shot: str, task: str) -> int:
	"""Get a free version of a scene name"""
	version_list = []

	for file in folder.glob("*.hip"):
		parts = parse_scene_name(file.name)
		if parts is None:
			continue
		file_shot, file_task, file_version = parts
		if file_shot != shot or file_task != task:
			continue
		version_list.append(file_version)

	return max(version_list, default=0) + 1



if __name__ == "__main__":
	test_folder = Path(__file__).parent.parent / "Hip" / "test_versions"
	print(get_next_version(test_folder, "sh010", "fx"))
	print(get_next_version(test_folder, "sh010", "anim"))
	print(get_next_version(test_folder, "sh030", "fx"))