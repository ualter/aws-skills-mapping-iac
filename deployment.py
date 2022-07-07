from typing import Any

from aws_cdk import core as cdk

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
        **kwargs: Any,
    ):

        super().__init__(scope, id_, **kwargs)
        self.props = props

        stateful = cdk.Stack(self, "Stateful")
        # stateless = cdk.Stack(self, "Stateless")

        self.s3_website = BucketStaticWebSiteHosting(
            stateful,
            "WebSite",
            name=f"{props.s3_bucket_website_name()}",
            deploy_hello_world=False,
        )

        self.s3_bucket_website_name = cdk.CfnOutput(
            stateful,
            f"{AwsSkillsMappingProps.OUTPUT_KEY_S3_BUCKET_WEBSITE_NAME}-Id",
            value=self.s3_website.bucket.bucket_name,
            export_name=AwsSkillsMappingProps.OUTPUT_KEY_S3_BUCKET_WEBSITE_NAME,
        )
        self.s3_bucket_website_url = cdk.CfnOutput(
            stateful,
            f"{AwsSkillsMappingProps.OUTPUT_KEY_S3_BUCKET_WEBSITE_URL}-Id",
            value=self.s3_website.bucket.bucket_website_url,
            export_name=AwsSkillsMappingProps.OUTPUT_KEY_S3_BUCKET_WEBSITE_URL,
        )
