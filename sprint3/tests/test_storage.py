import pytest
import storage
from pathlib import Path
from colony import Colony


@pytest.fixture(scope="class")
def storage_colony() -> Colony:
    return Colony(colony_id="colony_storage-test", ant_count=6, food=67)


@pytest.fixture(scope="class")
def save_dir(tmp_path_factory) -> Path:
    temp_dir = tmp_path_factory.mktemp("storage_test")
    return temp_dir


class TestStorage:
    def test_save_colony(self, save_dir, storage_colony):
        assert save_dir.is_dir(), "someone fucked up making save_dir for test"
        assert not any(save_dir.iterdir()), "folder must be empty before test"

        file_save = storage.save_colony(colony=storage_colony, save_dir=save_dir)
        assert any(save_dir.iterdir()), "folder must not be empty after `save_colony`"

        assert file_save.is_file, "save must be json file"
        assert file_save.exists(), "somehow u made a file that don't exists che blia"
        assert file_save.stat().st_size > 0, "file should not be empty"

    def test_list_saves(self, save_dir, storage_colony):
        files = storage.list_saves(save_dir=save_dir)
        assert len(files) == 1, "test fixtures are broken or file is not made"
        assert any(f"{storage_colony.id}.json" == f.name for f in files), (
            "file has different name (not id+.json) or not exists"
        )

    def test_load_colony(self, save_dir, storage_colony):
        loaded_colony = storage.load_colony(
            filename=f"{storage_colony.id}.json", save_dir=save_dir
        )
        assert loaded_colony.to_dict() == storage_colony.to_dict(), (
            "colonies must be equal"
        )
