from typing import Any

from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_s3 as s3
from aws_cdk import core as cdk

from deployment import AwsSkillsMapping


class AwsSkillsMappingPipeline(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        id_: str,
        **kwargs: Any,
    ):

        super().__init__(scope, id_, **kwargs)
        self._pipeline = codepipeline.Pipeline(self, id_)
        self._source_output = codepipeline.Artifact()
        self._dist_output = codepipeline.Artifact()

        self._add_source_stage()
        self._add_build_stage(self)

    def _add_source_stage(self) -> None:
        source_stage = self._pipeline.add_stage(stage_name="Source")
        source_stage.add_action(
            codepipeline_actions.GitHubSourceAction(
                action_name="GitHub",
                owner="ualter",
                repo="aws-skills-mapping-app",
                branch="v0.0.2",
                oauth_token=cdk.SecretValue.secrets_manager("github-ualter"),
                output=self._source_output,
                run_order=1
                # trigger= https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codepipeline_actions/GitHubTrigger.html#aws_cdk.aws_codepipeline_actions.GitHubTrigger
            )
        )

    def _add_build_stage(self, scope: cdk.Construct) -> None:
        build_stage = self._pipeline.add_stage(stage_name="Build")
        build_stage.add_action(
            codepipeline_actions.CodeBuildAction(
                action_name="CodeBuild",
                project=codebuild.PipelineProject(
                    scope,
                    "ProjectName",
                    build_spec=codebuild.BuildSpec.from_source_filename(
                        "./codebuild/buildspec.yaml"
                    ),
                ),
                input=self._source_output,
                outputs=[self._dist_output],
                run_order=2,
            )
        )

    def add_approval_stage(self) -> None:
        approval_stage = self._pipeline.add_stage(stage_name="Approve")
        approval_stage.add_action(
            codepipeline_actions.ManualApprovalAction(action_name="Approve")
        )

    def add_deploy_stage(self, stage: AwsSkillsMapping) -> None:

        # target_bucket = s3.Bucket.from_bucket_name(
        #     self,
        #     f"bucket-{stage.props.stage_name()}",
        #     stage.props.s3_bucket_website_name(),
        # )

        target_bucket = s3.Bucket.from_bucket_attributes(
            self,
            f"bucket-{stage.props.stage_name()}",
            bucket_name=stage.props.s3_bucket_website_name(),
            region=stage.props.env.region,
        )

        deploy_stage = self._pipeline.add_stage(
            stage_name=f"Deploy_{stage.props.stage_name().upper()}"
        )
        deploy_stage.add_action(
            codepipeline_actions.S3DeployAction(
                action_name="S3Deploy",
                bucket=target_bucket,
                input=self._dist_output,
            )
        )
