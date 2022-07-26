import abc

from aws_cdk import core as cdk

from configuration import ConfigurationLoader
from configuration import ConfigurationPipeline
from stages import Stages

# STAGES Environments
# Simply, composed of:
#  - AWS Account
#  - AWS Region

# All the values/configuration are loaded from YAML Files using the ConfigurationLoader


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


# STAGES Properties
# Information/properties for services/resources in each defined stages
#   Example of properties defined by Stage:
#    - Bucket name
#    - DynamoDB Billing Mode
#    - API Gateway throttling

# Abstract Stage
class AwsSkillsMappingConfig(cdk.StageProps):
    KEY_APP = "App-AwsSkillsMapping"
    KEY_S3_BUCKET_WEBSITE_NAME = f"{KEY_APP}-S3-Bucket-Website-Name"
    KEY_S3_BUCKET_WEBSITE_URL = f"{KEY_APP}-S3-Bucket-Website-Url"
    KEY_API_URL = f"{KEY_APP}-S3-Api-Url"

    def __init__(self, *, env: cdk.Environment) -> None:
        super().__init__(env=env, outdir=None)

        self.config_loader = ConfigurationLoader()
        self.configuration = self.config_loader.get_configuration_stage(self.stage())

    # type ignore
    def s3_bucket_website_name(self) -> str:
        default_config = self.config_loader.get_configuration_stage(Stages.DEFAULT)
        bucket_website_name_prefix = default_config.WebSite.BucketPrefix

        if isinstance(self.env, cdk.Environment):  # avoid mypy error checking
            return f"{bucket_website_name_prefix}-{self.env.account}-{self.env.region}-{self.stage().value}"
        raise ValueError(
            "Somethings very wrong! The self.env of AwsSkillsMappingProps Class, is not of type cdk.Environment, it must be!"
        )

    @abc.abstractmethod
    def stage(self) -> Stages:
        pass


# Dev
class AwsSkillsMappingConfigDev(AwsSkillsMappingConfig):
    def __init__(self) -> None:
        super().__init__(env=Environments()._DEV_ENV)

    def stage(self) -> Stages:
        return Stages.DEV


# PreProd
class AwsSkillsMappingConfigPreProd(AwsSkillsMappingConfig):
    def __init__(self) -> None:
        super().__init__(env=Environments()._PREPROD_ENV)

    def stage(self) -> Stages:
        return Stages.PREPROD


# Prod
class AwsSkillsMappingConfigProd(AwsSkillsMappingConfig):
    def __init__(self) -> None:
        super().__init__(env=Environments()._PROD_ENV)

    def stage(self) -> Stages:
        return Stages.PROD


# Pipeline
class AwsSkillsMappingConfigPipeline:
    def __init__(self) -> None:
        self.env = Environments()._PIPELINE_ENV
        self.configuration: ConfigurationPipeline = (
            ConfigurationLoader().get_configuration_pipeline()
        )
