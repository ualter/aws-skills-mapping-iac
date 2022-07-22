from typing import Any, List

from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_s3 as s3
from aws_cdk import core as cdk

from api.infrastructure import AwsSkillsMappingApi
from environment import AwsSkillsMappingConfig
from environment import PipelineConfig
from s3.infrastructure import BucketStaticWebSiteHosting

# Application that represents "The Platform" itself,
# all the infrastructure/services that must be
# provided by it.
# In this case our application will consist of two Stacks (unit of deployments):
# - Stateless
# - Stateful

#####################################
# Application IaC Deployment
# aws-skills-mapping
#####################################


class AwsSkillsMapping(cdk.Stage):
    def __init__(
        self,
        scope: cdk.Construct,
        id_: str,
        *,
        config: AwsSkillsMappingConfig,
        **kwargs: Any,
    ):

        super().__init__(scope, id_, **kwargs)
        self.config = config

        stateful = cdk.Stack(self, "Stateful")
        stateless = cdk.Stack(self, "Stateless")

        self.build_stateful(stateful)
        self.build_stateless(stateless)

    def build_stateful(self, stateful: cdk.Stack) -> None:
        self.s3_website = BucketStaticWebSiteHosting(
            stateful,
            "WebSite",
            name=f"{self.config.s3_bucket_website_name()}",
            deploy_hello_world=False,
        )

        self.s3_bucket_website_name = cdk.CfnOutput(
            stateful,
            f"{AwsSkillsMappingConfig.OUTPUT_KEY_S3_BUCKET_WEBSITE_NAME}-Id",
            value=self.s3_website.bucket.bucket_name,
            export_name=AwsSkillsMappingConfig.OUTPUT_KEY_S3_BUCKET_WEBSITE_NAME,
        )
        self.s3_bucket_website_url = cdk.CfnOutput(
            stateful,
            f"{AwsSkillsMappingConfig.OUTPUT_KEY_S3_BUCKET_WEBSITE_URL}-Id",
            value=self.s3_website.bucket.bucket_website_url,
            export_name=AwsSkillsMappingConfig.OUTPUT_KEY_S3_BUCKET_WEBSITE_URL,
        )

    def build_stateless(self, stateless: cdk.Stack) -> None:
        self.api = AwsSkillsMappingApi(
            stateless, "AwsSkillsMappingApi", _name_api="Aws-Skills-Mapping-Api"
        )
        self.api_url = cdk.CfnOutput(
            stateless,
            f"{AwsSkillsMappingConfig.OUTPUT_KEY_API_URL}-Id",
            value=self.api.skills_mapping_api.url,
            export_name=AwsSkillsMappingConfig.OUTPUT_KEY_API_URL,
        )


#####################################
# Application Pipeline Deployment
# aws-skills-mapping
#####################################


class AwsSkillsMappingPipeline(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        id_: str,
        *,
        pipe_config: PipelineConfig,
        **kwargs: Any,
    ):

        super().__init__(scope, id_, **kwargs)
        self._pipe_config = pipe_config
        self._pipeline = codepipeline.Pipeline(
            self, id_, pipeline_name="AwsSkillsMapping-Pipeline"
        )
        self._source_output = codepipeline.Artifact()
        self._dist_output = codepipeline.Artifact()

        self._add_source_stage()
        self._add_build_stage(self)

    def _add_source_stage(self) -> None:
        source_stage = self._pipeline.add_stage(stage_name="Source")

        source_stage.add_action(
            codepipeline_actions.GitHubSourceAction(
                action_name="GitHub",
                owner=self._pipe_config.configuration.Owner,
                repo=self._pipe_config.configuration.Name,
                branch=self._pipe_config.configuration.Branch,
                oauth_token=cdk.SecretValue.secrets_manager(
                    self._pipe_config.configuration.SecretNameOauthToken
                ),
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
                    "AwsSkillsMapping-Build",
                    build_spec=codebuild.BuildSpec.from_source_filename(
                        "./codebuild/buildspec.yaml"
                    ),
                    project_name="AwsSkillsMapping-Build",
                ),
                input=self._source_output,
                outputs=[self._dist_output],
                run_order=2,
            )
        )

    def add_approval_stage(self) -> None:
        approval_stage = self._pipeline.add_stage(stage_name="Approvals")

        emails_sre_team: List[str] = []
        for sre_member in self._pipe_config.configuration.SreTeam:
            emails_sre_team.append(sre_member.Email)
        sre_approval_action = codepipeline_actions.ManualApprovalAction(
            action_name="SRETeamApproval", notify_emails=emails_sre_team
        )
        approval_stage.add_action(sre_approval_action)

        emails_app_team: List[str] = []
        for app_member in self._pipe_config.configuration.ApplicationTeam:
            emails_app_team.append(app_member.Email)
        app_approval_action = codepipeline_actions.ManualApprovalAction(
            action_name="ApplicationTeamApproval", notify_emails=emails_app_team
        )
        approval_stage.add_action(app_approval_action)

    def add_deploy_stage(self, stage: AwsSkillsMapping) -> None:
        # this stage might be in a different region where this Pipeline Stack is deployed
        # ... also in another account - feature not implemented right now :-)
        stage_region = ""
        if (
            stage.config.env is not None and stage.config.env.region is not None
        ):  # avoid mypy checking error
            stage_region = stage.config.env.region

        target_bucket = s3.Bucket.from_bucket_attributes(
            self,
            f"bucket-{stage.config.stage().value}",
            bucket_name=stage.config.s3_bucket_website_name(),
            region=stage_region,
        )

        deploy_stage = self._pipeline.add_stage(
            stage_name=f"Deploy_{stage.config.stage().name}"
        )
        deploy_stage.add_action(
            codepipeline_actions.S3DeployAction(
                action_name="S3Deploy",
                bucket=target_bucket,
                input=self._dist_output,
            )
        )
