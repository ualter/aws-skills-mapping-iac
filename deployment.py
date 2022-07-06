from typing import Any

from aws_cdk import core as cdk

from devtools.infrastructure import AwsSkillsMappingPipeline
from environment import AwsSkillsMappingProps
from s3.infrastructure import BucketStaticWebSiteHosting

# Application that represents "The Platform" itself,
# all the infrastructure/services that must be
# provided by it.
# In this case our application will consist of two Stacks (unit of deployments):
# - Stateless
# - Stateful


class AwsSkillsMapping(cdk.Stage):
    def __init__(
        self,
        scope: cdk.Construct,
        id_: str,
        *,
        props: AwsSkillsMappingProps,
        **kwargs: Any
    ):

        super().__init__(scope, id_, **kwargs)

        stateful = cdk.Stack(self, "Stateful")
        self.s3_website = BucketStaticWebSiteHosting(
            stateful, "WebSite", name="ualterjuniorawsskillsmapping"
        )

        stateless = cdk.Stack(self, "Stateless")
        self.pipeline = AwsSkillsMappingPipeline(
            stateless,
            "AwsSkillsMapping",
            name="Aws-Skills-Mapping Pipeline",
            bucket_deploy_website=self.s3_website.bucket,
        )
