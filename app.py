#!/usr/bin/env python3
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import core as cdk

import constants
from deployment import AwsSkillsMapping
from deployment import AwsSkillsMappingPipeline
from environment import AwsSkillsMappingConfig
from environment import AwsSkillsMappingConfigDev
from environment import AwsSkillsMappingConfigPipeline
from environment import AwsSkillsMappingConfigPreProd

app = cdk.App()

# IaC DEVELOPMENT Stage
dev_config = AwsSkillsMappingConfigDev()
dev_stage = AwsSkillsMapping(
    app,
    f"{constants.CDK_APP_NAME}-{dev_config.stage().name}",
    config=dev_config,
    env=dev_config.env,
)

# IaC PREPROD Stage
preprod_config = AwsSkillsMappingConfigPreProd()
preprod_stage = AwsSkillsMapping(
    app,
    f"{constants.CDK_APP_NAME}-{preprod_config.stage().name}",
    config=preprod_config,
    env=preprod_config.env,
)

# PIPELINE Application: aws-skills-mapping
pipeline_config = AwsSkillsMappingConfigPipeline()
pipeline_config.environment_variables = {
    "AWS_SKILLS_MAPPING_API_URL": codebuild.BuildEnvironmentVariable(
        value=cdk.Fn.import_value(AwsSkillsMappingConfig.OUTPUT_KEY_API_URL)
    )
}
app_pipeline = AwsSkillsMappingPipeline(
    app,
    "AwsSkillsMapping-PIPELINE",
    pipe_config=pipeline_config,
    env=pipeline_config.env,
)


app_pipeline.add_deploy_stage(dev_stage)
# app_pipeline.add_approval_stage()
# app_pipeline.add_deploy_stage(preprod_stage)


# # PRE-PRODUCTION and PRODUCTION Stage will be deployed using this Pipeline
# # Our Pipeline application will create the infra for CodePipeline and CodeBuild
# pip = PipelineProps()
# Pipeline(
#     app,
#     f"{constants.CDK_APP_NAME}-Pipeline",
#     env=pip.env,  # We will deploy the Pipeline in Development Environment
# )

app.synth()
