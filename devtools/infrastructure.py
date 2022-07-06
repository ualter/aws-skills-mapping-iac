import pathlib

from aws_cdk import core as cdk
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions



class AwsSkillsMappingPipeline(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id_: str, *, name: str, bucket_deploy_website: s3.Bucket):
        super().__init__(scope, id_)

        pipeline = codepipeline.Pipeline(self, "AwsSkillsMapping-Pipeline")

        source_output = codepipeline.Artifact()

        source_stage = pipeline.add_stage(stage_name="Source")
        source_stage.add_action(codepipeline_actions.GitHubSourceAction(
            action_name="GitHub",
            owner="ualter",
            repo="aws-skills-mapping-app",
            branch="v0.0.2",
            oauth_token=cdk.SecretValue.secrets_manager("github-ualter"),
            output=source_output,
            run_order=1
            # trigger= https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codepipeline_actions/GitHubTrigger.html#aws_cdk.aws_codepipeline_actions.GitHubTrigger
        ))

        build_stage = pipeline.add_stage(stage_name="Build")
        build_stage.add_action(codepipeline_actions.CodeBuildAction(
                action_name="CodeBuild",
                project=codebuild.PipelineProject(self, "ProjectName",  
                    build_spec=codebuild.BuildSpec.from_source_filename("./codebuild/buildspec.yaml")
                    # build_spec=codebuild.BuildSpec.from_object({ # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codebuild/PipelineProjectProps.html#pipelineprojectprops
                    #     "version": "0.2",
                    # })
                ),
                input=source_output,
                run_order=2,
            )
        )
        
        # target_bucket = s3.Bucket.from_bucket_name(self, "imported-bucket-from-name","ualterjuniorawsskillsmapping")
        deploy_stage = pipeline.add_stage(stage_name="Deploy")
        deploy_stage.add_action(codepipeline_actions.S3DeployAction(
                action_name="S3Deploy",
                bucket=bucket_deploy_website,
                input=source_output,
            )
        )


        


