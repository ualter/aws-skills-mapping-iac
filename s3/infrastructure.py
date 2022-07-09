import pathlib

from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3deploy
from aws_cdk import core as cdk


class BucketHelmRepo(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id_: str, *, name: str):
        super().__init__(scope, id_)

        self.bucket = s3.Bucket(
            self,
            "Bucket",
            bucket_name=name,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )


class BucketStaticWebSiteHosting(cdk.Construct):
    def __init__(
        self, scope: cdk.Construct, id_: str, *, name: str, deploy_hello_world: bool
    ):
        super().__init__(scope, id_)

        self.bucket = s3.Bucket(
            self,
            "BucketStaticWebSiteHosting",
            bucket_name=name,
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            website_index_document="index.html",
            website_error_document="index.html",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        if deploy_hello_world:
            source_dir = pathlib.Path(__file__).resolve().parent.joinpath("runtime")
            s3deploy.BucketDeployment(
                self,
                "DeployIndexHtmlHelloWorld",
                sources=[s3deploy.Source.asset(str(source_dir))],
                destination_bucket=self.bucket,
            )
