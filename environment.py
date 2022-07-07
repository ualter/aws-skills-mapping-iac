import abc
import os
from dataclasses import dataclass
from enum import Enum

from aws_cdk import core as cdk


class Stages(Enum):
    DEV = "dev"
    PREPROD = "preprod"
    PROD = "prod"


@dataclass
class Environment:
    Account_Id: str
    Region: str


class Environments:
    def __init__(self) -> None:
        self._DEV_ENV = cdk.Environment(
            account=os.environ.get("CDK_DEVELOPMENT_ACCOUNT", "dev-acc-notset"),
            region=os.environ.get("CDK_DEVELOPMENT_REGION", "dev-region-notset"),
        )
        self._PREPROD_ENV = cdk.Environment(
            account=os.environ.get("CDK_PREPROD_ACCOUNT", "pprod-acc-notset"),
            region=os.environ.get("CDK_PREPROD_REGION", "pprod-region-notset"),
        )
        self._PIPELINE_ENV = cdk.Environment(
            account=os.environ.get("CDK_PIPELINE_ACCOUNT", "pipeline-acc-notset"),
            region=os.environ.get("CDK_PIPELINE_REGION", "pipeline-region-notset"),
        )
        self._PROD_ENV = cdk.Environment(
            account=os.environ.get("CDK_PRODUCTION_ACCOUNT", "prod-acc-notset"),
            region=os.environ.get("CDK_PRODUCTION_REGION", "prod-region-notset"),
        )

    def dev_account(self) -> Environment:
        return Environment(Account_Id=self._DEV_ENV.account, Region=self._DEV_ENV.region)  # type: ignore

    def preprod_account(self) -> Environment:
        return Environment(Account_Id=self._PREPROD_ENV.account, Region=self._PREPROD_ENV.region)  # type: ignore

    def pipeline_account(self) -> Environment:
        return Environment(Account_Id=self._PIPELINE_ENV.account, Region=self._PIPELINE_ENV.region)  # type: ignore

    def prod_account(self) -> Environment:
        return Environment(Account_Id=self._PROD_ENV.account, Region=self._PROD_ENV.region)  # type: ignore


# STAGES Properties
# Runtime information/properties for the defined stages
#   Example of properties defind by Stage:
#    - Bucket name
#    - Database Name
#    - DynamoDB Billing Mode

# Abstract Stage
class AwsSkillsMappingProps(cdk.StageProps):
    OUTPUT_KEY_S3_BUCKET_WEBSITE_NAME = "S3-Bucket-Website-Name"
    OUTPUT_KEY_S3_BUCKET_WEBSITE_URL = "S3-Bucket-Website-Url"

    def __init__(self, *, env: cdk.Environment) -> None:
        super().__init__(env=env, outdir=None)

    # type ignore
    def s3_bucket_website_name(self) -> str:
        if isinstance(self.env, cdk.Environment):  # avoid mypy error checking
            return f"ualter-aws-skills-mapping-{self.env.account}-{self.env.region}-{self.stage_name()}"
        raise ValueError(
            "Somethings very wrong! The self.env of AwsSkillsMappingProps Class, is not of type cdk.Environment, it must be!"
        )

    @abc.abstractmethod
    def stage_name(self) -> str:
        pass


# Dev
class AwsSkillsMappingPropsDev(AwsSkillsMappingProps):
    def __init__(self) -> None:
        super().__init__(env=Environments()._DEV_ENV)

    def stage_name(self) -> str:
        return "dev"


# PreProd
class AwsSkillsMappingPropsPreProd(AwsSkillsMappingProps):
    def __init__(self) -> None:
        super().__init__(env=Environments()._PREPROD_ENV)

    def stage_name(self) -> str:
        return "preprod"


# Prod
class AwsSkillsMappingPropsProd(AwsSkillsMappingProps):
    def __init__(self) -> None:
        super().__init__(env=Environments()._PROD_ENV)

    def stage_name(self) -> str:
        return "prod"


# Pipeline Properties
class PipelineProps:
    def __init__(self) -> None:
        self.env = Environments()._PIPELINE_ENV
