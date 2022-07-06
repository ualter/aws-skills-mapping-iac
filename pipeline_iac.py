# # Info: https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html
# # "The construct CodePipeline is the construct that represents a CDK Pipeline that uses AWS CodePipeline as its deployment engine.
# #  When you instantiate CodePipeline in a stack, you define the source location for the pipeline (e.g. a GitHub repository)
# #  and the commands to build the app."

# from typing import Any

# from aws_cdk import aws_codebuild as codebuild
# from aws_cdk import aws_codestarnotifications as notifications
# from aws_cdk import aws_sns as sns
# from aws_cdk import core as cdk
# from aws_cdk import pipelines

# import constants
# import utils
# from deployment import AwsSkillsMapping
# from environment import AwsSkillsMappingPropsPreProd
# from environment import AwsSkillsMappingPropsProd
# from environment import Environments
# from repository import GitHubConnection
# from repository import Repositories


# class Pipeline(cdk.Stack):
#     def __init__(self, scope: cdk.Construct, id_: str, **kwargs: Any):
#         super().__init__(scope, id_, **kwargs)

#         self._create_pipeline_stages()

#     def _create_pipeline_stages(self) -> None:
#         synth_codebuild_step = self._create_synth_codebuild_step()

#         codepipeline = pipelines.CodePipeline(
#             self,
#             "AwsSkillsMapping-CodePipeline",
#             cli_version=utils.cdk_version(),
#             cross_account_keys=False,
#             synth=synth_codebuild_step,
#             self_mutation=True,
#         )

#         self._add_preprod_stage(codepipeline)
#         self._add_manual_approvals_stage(codepipeline)
#         self._add_prod_stage(codepipeline)
#         self._add_notifications(codepipeline)

#     def _create_synth_codebuild_step(self) -> pipelines.CodeBuildStep:

#         git_hub_connection = Repositories().github_connection()

#         source = self._get_source_code(git_hub_connection)

#         synth_python_version = {
#             "phases": {
#                 "install": {
#                     "runtime-versions": {"python": constants.CDK_APP_PYTHON_VERSION},
#                     "commands": ["python --version"],
#                 }
#             }
#         }

#         synth_codebuild_step = pipelines.CodeBuildStep(
#             "Synth",
#             input=source,
#             partial_build_spec=codebuild.BuildSpec.from_object(synth_python_version),
#             env={
#                 "VIRTUAL_ENV": "yes",
#                 "CDK_PREPROD_ACCOUNT": Environments().preprod_account().Account_Id,
#                 "CDK_PREPROD_REGION": Environments().preprod_account().Region,
#                 "CDK_PIPELINE_ACCOUNT": Environments().pipeline_account().Account_Id,
#                 "CDK_PIPELINE_REGION": Environments().pipeline_account().Region,
#                 "CDK_PRODUCTION_ACCOUNT": Environments().prod_account().Account_Id,
#                 "CDK_PRODUCTION_REGION": Environments().prod_account().Region,
#                 "CDK_GITHUB_CONNECTION_ARN": git_hub_connection.ConnectionArn,
#                 "CDK_GITHUB_OWNER": git_hub_connection.Owner,
#                 "CDK_GITHUB_REPO": git_hub_connection.Repository,
#                 "CDK_GITHUB_TRUNK_BRANCH": git_hub_connection.TrunkBranch,
#             },
#             install_commands=[
#                 "npm install -g aws-cdk",
#                 # "pip install -r requirements.txt -r requirements-dev.txt",
#                 "pip install -r requirements.txt",
#             ],
#             commands=[
#                 # "./scripts/run-checks.sh",
#                 "cdk synth",
#             ],
#         )

#         return synth_codebuild_step

#     def _get_source_code(self, git_hub_connection: GitHubConnection) -> pipelines.CodePipelineSource:  # type: ignore
#         return pipelines.CodePipelineSource.connection(
#             f"{git_hub_connection.Owner}/{git_hub_connection.Repository}",
#             git_hub_connection.TrunkBranch,
#             connection_arn=git_hub_connection.ConnectionArn,
#         )

#     def _add_preprod_stage(self, codepipeline: pipelines.CodePipeline) -> None:
#         pre_production_props = AwsSkillsMappingPropsPreProd()
#         pre_production = AwsSkillsMapping(
#             self,
#             f"{constants.CDK_APP_NAME}-PreProd",
#             props=pre_production_props,
#             env=pre_production_props.env,
#         )

#         pre_production_stage = codepipeline.add_stage(pre_production)

#         pre_production_stage.add_post(
#             pipelines.ShellStep(
#                 "Test PreProd Helm Repo Bucket",
#                 env={"buck_name": pre_production.bucket_helm_repo.bucket.bucket_name},
#                 commands=["echo $buck_name"],
#             )
#         )

#     def _add_prod_stage(self, codepipeline: pipelines.CodePipeline) -> None:
#         prod_props = AwsSkillsMappingPropsProd()
#         production = AwsSkillsMapping(
#             self,
#             f"{constants.CDK_APP_NAME}-Prod",
#             props=prod_props,
#             env=prod_props.env,
#         )

#         production_stage = codepipeline.add_stage(production)

#         production_stage.add_post(
#             pipelines.ShellStep(
#                 "Test Prod Helm Repo Bucket",
#                 env={"buck_name": production.bucket_helm_repo.bucket.bucket_name},
#                 commands=["echo $buck_name"],
#             )
#         )

#     def _add_manual_approvals_stage(self, codepipeline: pipelines.CodePipeline) -> None:
#         approval_stage = codepipeline.add_wave("Approvals")
#         approval_stage.add_pre(pipelines.ManualApprovalStep("Application Team Approval"))  # type: ignore
#         approval_stage.add_pre(pipelines.ManualApprovalStep("SRE Team Approval"))

#     def _add_notifications(self, codepipeline: pipelines.CodePipeline) -> None:
#         codepipeline.build_pipeline()

#         topic = sns.Topic(self, "TopicManualApprovalNeeded")

#         sns.Subscription(
#             self,
#             "Subscription-SRE-Team-Member",
#             topic=topic,
#             endpoint="ualter.junior@gmail.com",
#             protocol=sns.SubscriptionProtocol.EMAIL,
#         )

#         notifications.NotificationRule(
#             self,
#             "ManualApprovalNeeded",
#             source=codepipeline.pipeline,
#             # Checks here for events: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events
#             events=["codepipeline-pipeline-manual-approval-needed"],
#             targets=[topic],
#         )
