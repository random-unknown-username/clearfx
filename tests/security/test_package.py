import pytest
from pathlib import Path
from clearfx.formats.package import PackageReader, PackageBuilder
import zipfile
from unittest.mock import MagicMock

def test_package_reader_size_limit(tmp_path, monkeypatch):
    # Mock stat to return a size greater than 10MB
    fake_stat = MagicMock()
    fake_stat.st_size = 11 * 1024 * 1024
    monkeypatch.setattr(Path, "stat", lambda self: fake_stat)

    with pytest.raises(ValueError, match="Archive too large"):
        PackageReader(tmp_path / "dummy.zip")

def test_package_reader_path_traversal(tmp_path, monkeypatch):
    # Mock stat to return safe size
    fake_stat = MagicMock()
    fake_stat.st_size = 1024
    monkeypatch.setattr(Path, "stat", lambda self: fake_stat)

    # Mock zipfile to return a malicious entry
    fake_zip = MagicMock()
    fake_info = MagicMock()
    fake_info.filename = "../malicious.sh"
    fake_zip.infolist.return_value = [fake_info]

    monkeypatch.setattr(zipfile, "ZipFile", lambda *args, **kwargs: fake_zip)
    
    with pytest.raises(ValueError, match="Path traversal detected"):
        PackageReader(tmp_path / "dummy.zip")

def test_package_reader_absolute_path_traversal(tmp_path, monkeypatch):
    fake_stat = MagicMock()
    fake_stat.st_size = 1024
    monkeypatch.setattr(Path, "stat", lambda self: fake_stat)

    fake_zip = MagicMock()
    fake_info = MagicMock()
    fake_info.filename = "/etc/passwd"
    fake_zip.infolist.return_value = [fake_info]

    monkeypatch.setattr(zipfile, "ZipFile", lambda *args, **kwargs: fake_zip)
    
    with pytest.raises(ValueError, match="Path traversal detected"):
        PackageReader(tmp_path / "dummy.zip")

def test_package_builder_asset_size_limit():
    builder = PackageBuilder()
    # Mock an asset larger than 5MB
    with pytest.raises(ValueError, match="Asset large_asset too large"):
        builder.add_asset("large_asset", b"0" * (6 * 1024 * 1024))
