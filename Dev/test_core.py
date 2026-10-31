import os

from core import parse_scene_name, build_scene_name, get_next_version

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
    names = ["sh010_fx_v001.hip","sh010_fx_v003.hip","sh010_fx_v005.hip","sh010_fx_v004.json","sh020_fx_v009.hip",
             "sh010_anim_v007.hip","untitled.hip"]
    for name in names:
        (folder / name).touch()


def test_next_version_finds_highest(tmp_path):
    create_version_files(tmp_path)
    assert get_next_version(tmp_path, "sh010", "fx") == 6

def test_next_version_filters_task(tmp_path):
    create_version_files(tmp_path)
    assert get_next_version(tmp_path,"sh010", "anim") == 8

def test_next_version_empty_folder(tmp_path):
    assert get_next_version(tmp_path,"sh030", "fx") == 1