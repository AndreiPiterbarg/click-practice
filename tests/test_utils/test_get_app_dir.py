import os
import sys

import pytest

import click


@pytest.fixture
def home(monkeypatch, tmp_path):
    home = str(tmp_path / "home")
    monkeypatch.setenv("HOME", home)
    monkeypatch.setenv("USERPROFILE", home)

    for name in ("XDG_CONFIG_HOME", "APPDATA", "LOCALAPPDATA"):
        monkeypatch.delenv(name, raising=False)

    monkeypatch.setattr(click.utils, "WIN", False)
    monkeypatch.setattr(sys, "platform", "linux")
    return home


@pytest.fixture
def windows(monkeypatch, home):
    monkeypatch.setattr(click.utils, "WIN", True)
    monkeypatch.setattr(sys, "platform", "win32")


@pytest.mark.parametrize("roaming", [True, False])
def test_linux_default(home, roaming):
    expected = os.path.join(home, ".config", "foo-bar")
    assert click.get_app_dir("Foo Bar", roaming=roaming) == expected


def test_linux_xdg_config_home(monkeypatch, home, tmp_path):
    xdg = str(tmp_path / "xdg")
    monkeypatch.setenv("XDG_CONFIG_HOME", xdg)
    assert click.get_app_dir("Foo Bar") == os.path.join(xdg, "foo-bar")


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_force_posix(monkeypatch, home, tmp_path, platform):
    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    expected = os.path.join(home, ".foo-bar")
    assert click.get_app_dir("Foo Bar", force_posix=True) == expected


def test_macos(monkeypatch, home):
    monkeypatch.setattr(sys, "platform", "darwin")
    expected = os.path.join(home, "Library", "Application Support", "Foo Bar")
    assert click.get_app_dir("Foo Bar") == expected


@pytest.mark.parametrize(
    ("roaming", "expected_key"),
    [(True, "APPDATA"), (False, "LOCALAPPDATA")],
)
@pytest.mark.usefixtures("windows")
def test_windows(monkeypatch, tmp_path, roaming, expected_key):
    folders = {
        "APPDATA": str(tmp_path / "Roaming"),
        "LOCALAPPDATA": str(tmp_path / "Local"),
    }

    for name, value in folders.items():
        monkeypatch.setenv(name, value)

    expected = os.path.join(folders[expected_key], "Foo Bar")
    assert click.get_app_dir("Foo Bar", roaming=roaming) == expected


@pytest.mark.parametrize(
    ("roaming", "other_key"),
    [(True, None), (False, None), (True, "LOCALAPPDATA"), (False, "APPDATA")],
)
@pytest.mark.usefixtures("windows")
def test_windows_unset_falls_back_to_home(
    monkeypatch, home, tmp_path, roaming, other_key
):
    if other_key is not None:
        monkeypatch.setenv(other_key, str(tmp_path / "other"))

    expected = os.path.join(home, "Foo Bar")
    assert click.get_app_dir("Foo Bar", roaming=roaming) == expected


@pytest.mark.usefixtures("windows")
def test_windows_ignores_force_posix(monkeypatch, tmp_path):
    appdata = str(tmp_path / "Roaming")
    monkeypatch.setenv("APPDATA", appdata)
    expected = os.path.join(appdata, "Foo Bar")
    assert click.get_app_dir("Foo Bar", force_posix=True) == expected
