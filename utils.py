import json
import pathlib    
from typing import Any
    

def cdk_version() -> str:
    file_package = (
        pathlib.Path(__file__).resolve().parent.joinpath("package.json")
    )
    with open(file_package) as json_file:
        json_content = json.load(json_file)
    version = str(json_content["devDependencies"]["aws-cdk"])
    return version

def load_json_file(file_name: str) -> Any:
    f = (
        pathlib.Path(__file__).resolve().parent.joinpath(file_name)
    )
    with open(f) as json_file:
        json_content = json.load(json_file)
    return json_content

def pretty_print(json_content: Any) -> None:
    print(json.dumps(json_content, indent=4, sort_keys=False))