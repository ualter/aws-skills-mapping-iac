from typing import Any, Dict, List, Mapping

from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from aws_cdk import core as cdk

import constants
from api.infrastructure import ApiAwsSkillsMapping
from custom_resources import SSMReader
from database.infrastructure import DynamoDBAwsSkillsMapping
from environment import AwsSkillsMappingConfig
from environment import AwsSkillsMappingConfigPipeline
from website.infrastructure import BucketStaticWebSiteHosting

# CDK Application that represents/model "the platform" for a specific application/solution,
# that is, all the infrastructure/services that must be provided for the application/solution (in this case, AWS Skills Mapping Application).
#
# Here, we have decided that our application infrasctructure will consist of two Stacks (unit of deployments):
#  - Stateless
#  - Stateful

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

        self.stateful = cdk.Stack(self, "Stateful")
        self.stateless = cdk.Stack(self, "Stateless")

        self.build_stateful()
        self.build_stateless()

    def build_stateful(self) -> None:
        self.s3_website = BucketStaticWebSiteHosting(
            self.stateful,
            "WebSite",
            name=f"{self.config.s3_bucket_website_name()}",
            deploy_hello_world=False,
        )

        self.database = DynamoDBAwsSkillsMapping(
            self.stateful,
            "Database",
            table_name="AwsSkillsMappingTable",
            load_initial_data=True,
        )
        if hasattr(self, "api") and self.api is not None:
            self.database.table.grant_read_data(self.api.lambda_handler)

        # Bucket to save my Artifacts used by Pipeline
        # awsskillsmapping-pipeline-artifacts-ACCOUNT-REGION
        self.my_artifacts_bucket = s3.Bucket(  # type: ignore
            self.stateful,
            f"{self.config.s3_bucket_my_artifacts_bucket_name()}-Id",
            bucket_name=self.config.s3_bucket_my_artifacts_bucket_name(),
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        self.s3_bucket_website_name = cdk.CfnOutput(
            self.stateful,
            f"{AwsSkillsMappingConfig.KEY_S3_BUCKET_WEBSITE_NAME}-Id",
            value=self.s3_website.bucket.bucket_name,
            export_name=AwsSkillsMappingConfig.KEY_S3_BUCKET_WEBSITE_NAME,
        )
        self.s3_bucket_website_url = cdk.CfnOutput(
            self.stateful,
            f"{AwsSkillsMappingConfig.KEY_S3_BUCKET_WEBSITE_URL}-Id",
            value=self.s3_website.bucket.bucket_website_url,
            export_name=AwsSkillsMappingConfig.KEY_S3_BUCKET_WEBSITE_URL,
        )

    def build_stateless(self) -> None:
        self.api = ApiAwsSkillsMapping(
            self.stateless,
            f"{constants.CDK_APP_NAME}Api",
            _name_api=f"{constants.CDK_APP_NAME}-Api",
        )
        if hasattr(self, "database") and self.database is not None:
            self.database.table.grant_read_data(self.api.lambda_handler)

        self._save_parameter(
            self.stateless,
            AwsSkillsMappingConfig.KEY_API_URL,
            self.api.skills_mapping_api.url,
        )

        self.api_url = cdk.CfnOutput(
            self.stateless,
            f"{AwsSkillsMappingConfig.KEY_API_URL}-Id",
            value=self.api.skills_mapping_api.url,
            export_name=AwsSkillsMappingConfig.KEY_API_URL,
        )

    def _save_parameter(
        self, scope: cdk.Stack, parameter_name: str, parameter_value: str
    ) -> None:
        ssm.StringParameter(
            scope,
            f"Parameter-{parameter_name}",
            parameter_name=parameter_name,
            string_value=parameter_value,
            type=ssm.ParameterType.STRING,
        )


#
# Below, using aws-cdk we also build an CI/CD Pipeline in AWS (CodeBuild, CodePipeline)
# for the AWS Skills Mapping (an Angular application)
#

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
        pipe_config: AwsSkillsMappingConfigPipeline,
        artifacts_buckets: Mapping[str, str],
        **kwargs: Any,
    ):

        super().__init__(scope, id_, **kwargs)
        self._scope = self
        self._pipe_config = pipe_config

        # Add Bucket for Artifacts in the same Region of the Pipeline
        cross_region_replication_buckets: Dict[str, s3.IBucket] = {}
        for region in artifacts_buckets:
            bucket_name = artifacts_buckets[region]
            cross_region_replication_buckets[region] = s3.Bucket.from_bucket_attributes(
                self,
                f"bucket-{bucket_name}-Id",
                bucket_name=bucket_name,
                region=region,
            )

        self._pipeline = codepipeline.Pipeline(
            self,
            id_,
            pipeline_name=f"{constants.CDK_APP_NAME}-Pipeline",
            cross_region_replication_buckets=cross_region_replication_buckets,
        )
        self._pipeline.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        self._source_output = codepipeline.Artifact()
        self._add_source_stage()

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

    def add_deploy_stage(
        self,
        stage: AwsSkillsMapping,
        stage_config: AwsSkillsMappingConfig,
    ) -> None:

        # Read Cross Stack (Region) Dynamic Parameters
        ssm_reader_api_url = SSMReader(
            self,
            f"SSMReader-{stage.config.stage().name}",
            parameter_name=AwsSkillsMappingConfig.KEY_API_URL,
            region=stage_config.env.region,  # type: ignore
        )
        _environment_variables = {
            "AWS_SKILLS_MAPPING_API_URL": codebuild.BuildEnvironmentVariable(
                value=ssm_reader_api_url.getParameterValue()
            ),
            "AWS_SKILLS_MAPPING_STAGE": codebuild.BuildEnvironmentVariable(
                value=f"{stage.config.stage().name.lower()}"
            ),
        }

        _dist_output = codepipeline.Artifact()

        build_stage = self._pipeline.add_stage(
            stage_name=f"Build-{stage.config.stage().name}"
        )
        build_stage.add_action(
            codepipeline_actions.CodeBuildAction(
                action_name=f"CodeBuild-{stage.config.stage().name}",
                project=codebuild.PipelineProject(
                    self._scope,
                    f"{constants.CDK_APP_NAME}-Build-{stage.config.stage().name}",
                    build_spec=codebuild.BuildSpec.from_source_filename(
                        "./codebuild/buildspec.yaml"
                    ),
                    project_name=f"{constants.CDK_APP_NAME}-Build-{stage.config.stage().name}",
                    environment_variables=_environment_variables,
                ),
                input=self._source_output,
                outputs=[_dist_output],
                run_order=2,
            )
        )

        stage_region = stage.config.env.region  # type: ignore

        target_bucket = s3.Bucket.from_bucket_attributes(
            self,
            f"bucket-{stage.config.stage().value}",
            bucket_name=stage.config.s3_bucket_website_name(),
            region=stage_region,
        )

        deploy_stage = self._pipeline.add_stage(
            stage_name=f"Deploy-{stage.config.stage().name}"
        )
        deploy_stage.add_action(
            codepipeline_actions.S3DeployAction(
                action_name="S3Deploy",
                bucket=target_bucket,
                input=_dist_output,
            )
        )
