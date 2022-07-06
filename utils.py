import json
import pathlib    
    

def cdk_version() -> str:
    file_package = (
        pathlib.Path(__file__).resolve().parent.joinpath("package.json")
    )
    with open(file_package) as json_file:
        json_content = json.load(json_file)
    version = str(json_content["devDependencies"]["aws-cdk"])
    return version