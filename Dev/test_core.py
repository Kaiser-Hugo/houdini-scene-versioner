from pathlib import Path

from core import (parse_scene_name, build_scene_name, get_next_version, is_valid_name_part, build_scene_folder,
				  read_metadata, write_metadata)


def test_parse_valid_name():
	assert parse_scene_name("sh010_fx_v003.hip") == ("sh010", "fx", 3)


def test_parse_invalid_name():
	assert parse_scene_name("untitled.hip") is None


def test_parse_rejects_uppercase():
	assert parse_scene_name("SH010_fx_v003.hip") is None


def test_parse_rejects_missing_v():
	assert parse_scene_name("sh010_fx_003.hip") is None


def test_build_scene_name():
	assert build_scene_name("sh010", "fx", 4) == "sh010_fx_v004.hip"


def test_parse_build_roundtrip():
	assert parse_scene_name(build_scene_name("sh010", "fx", 4)) == ("sh010", "fx", 4)


def create_version_files(folder):
	names = ["sh010_fx_v001.hip", "sh010_fx_v003.hip", "sh010_fx_v005.hip", "sh010_fx_v004.json", "sh020_fx_v009.hip",
			 "sh010_anim_v007.hip", "untitled.hip"]
	for name in names:
		(folder / name).touch()


def test_next_version_finds_highest(tmp_path):
	create_version_files(tmp_path)
	assert get_next_version(tmp_path, "sh010", "fx") == 6


def test_next_version_filters_task(tmp_path):
	create_version_files(tmp_path)
	assert get_next_version(tmp_path, "sh010", "anim") == 8


def test_next_version_empty_folder(tmp_path):
	assert get_next_version(tmp_path, "sh030", "fx") == 1


def test_valid_name_part_accepts_lowercase():
	assert is_valid_name_part("sh010")


def test_valid_name_part_rejects_uppercase():
	assert not is_valid_name_part("FX")


def test_valid_name_part_rejects_space():
	assert not is_valid_name_part("sh 010")


def test_valid_name_part_rejects_dash():
	assert not is_valid_name_part("fx-sim")


def test_valid_name_part_rejects_empty():
	assert not is_valid_name_part("")


def test_build_scene_folder():
	assert build_scene_folder(Path("/projet"), "sh010", "fx") == Path("/projet/shots/sh010/fx")


def test_metadata_roundtrip(tmp_path):
	metadata = {"shot": "shot010", "task": "fx", "version": 2}
	json_path = tmp_path / "test.json"

	write_metadata(json_path, metadata)

	assert read_metadata(json_path) == metadata


def test_read_metadata_missing_file(tmp_path):
	assert read_metadata(tmp_path / "missing.json") == {}


def test_metadata_keeps_accents(tmp_path):
	metadata = {"shot": "shot010", "task": "fx", "version": 2, "comment": "éclairage corrigé"}
	json_path = tmp_path / "test.json"

	write_metadata(json_path, metadata)

	assert read_metadata(json_path) == metadata