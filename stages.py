from enum import Enum

class Stages(Enum):
    DEV      = "dev"
    PREPROD  = "preprod"
    PROD     = "prod"

    DEFAULT  = "default"
    PIPELINE = "pipeline"