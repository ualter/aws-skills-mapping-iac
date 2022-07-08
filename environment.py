import abc

from aws_cdk import core as cdk

from configuration import ConfigurationLoader
from stages import Stages

# from dataclasses import dataclass


# @dataclass
# class Environment:
#     Account_Id: str
#     Region: str


class Environments:
    def __init__(self) -> None:

        config_loader = ConfigurationLoader()
        dev_config = config_loader.get_configuration_stage(Stages.DEV)
        preprod_config = config_loader.get_configuration_stage(Stages.PREPROD)
        prod_config = config_loader.get_configuration_stage(Stages.PROD)
        pipeline_config = config_loader.get_configuration_pipeline()

        self._DEV_ENV = cdk.Environment(
            account=dev_config.Environment.Account,
            region=dev_config.Environment.Region,
        )
        self._PREPROD_ENV = cdk.Environment(
            account=preprod_config.Environment.Account,
            region=preprod_config.Environment.Region,
        )
        self._PIPELINE_ENV = cdk.Environment(
            account=pipeline_config.Environment.Account,
            region=pipeline_config.Environment.Region,
        )
        self._PROD_ENV = cdk.Environment(
            account=prod_config.Environment.Account,
            region=prod_config.Environment.Region,
        )

    # def dev_account(self) -> Environment:
    #     return Environment(Account_Id=self._DEV_ENV.account, Region=self._DEV_ENV.region)  # type: ignore

    # def preprod_account(self) -> Environment:
    #     return Environment(Account_Id=self._PREPROD_ENV.account, Region=self._PREPROD_ENV.region)  # type: ignore

    # def pipeline_account(self) -> Environment:
    #     return Environment(Account_Id=self._PIPELINE_ENV.account, Region=self._PIPELINE_ENV.region)  # type: ignore

    # def prod_account(self) -> Environment:
    #     return Environment(Account_Id=self._PROD_ENV.account, Region=self._PROD_ENV.region)  # type: ignore


# STAGES Properties
# Runtime information/properties for the defined stages
#   Example of properties defind by Stage:
#    - Bucket name
#    - Database Name
#    - DynamoDB Billing Mode

# Abstract Stage
class AwsSkillsMappingConfig(cdk.StageProps):
    OUTPUT_KEY_S3_BUCKET_WEBSITE_NAME = "S3-Bucket-Website-Name"
    OUTPUT_KEY_S3_BUCKET_WEBSITE_URL = "S3-Bucket-Website-Url"

    def __init__(self, *, env: cdk.Environment) -> None:
        super().__init__(env=env, outdir=None)

        self.config_loader = ConfigurationLoader()

    # type ignore
    def s3_bucket_website_name(self) -> str:
        default_config = self.config_loader.get_configuration_stage(Stages.DEFAULT)
        bucket_website_name_prefix = default_config.WebSite.BucketPrefix

        if isinstance(self.env, cdk.Environment):  # avoid mypy error checking
            return f"{bucket_website_name_prefix}-{self.env.account}-{self.env.region}-{self.stage_name()}"
        raise ValueError(
            "Somethings very wrong! The self.env of AwsSkillsMappingProps Class, is not of type cdk.Environment, it must be!"
        )

    @abc.abstractmethod
    def stage_name(self) -> str:
        pass


# Dev
class AwsSkillsMappingConfigDev(AwsSkillsMappingConfig):
    def __init__(self) -> None:
        super().__init__(env=Environments()._DEV_ENV)

    def stage_name(self) -> str:
        return Stages.DEV.value


# PreProd
class AwsSkillsMappingConfigPreProd(AwsSkillsMappingConfig):
    def __init__(self) -> None:
        super().__init__(env=Environments()._PREPROD_ENV)

    def stage_name(self) -> str:
        return Stages.PREPROD.value


# Prod
class AwsSkillsMappingConfigProd(AwsSkillsMappingConfig):
    def __init__(self) -> None:
        super().__init__(env=Environments()._PROD_ENV)

    def stage_name(self) -> str:
        return Stages.PROD.value


# Pipeline Properties
class PipelineConfig:
    def __init__(self) -> None:
        self.env = Environments()._PIPELINE_ENV
