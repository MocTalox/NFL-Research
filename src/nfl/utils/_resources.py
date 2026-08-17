from importlib.resources import files


def read_data_resource_files(file: str) -> str:
    resource = files("nfl.data") / "files" / file
    return resource.read_text(encoding="utf-8")
