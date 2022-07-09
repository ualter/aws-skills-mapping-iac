#!/usr/bin/env python3
from aws_cdk import core as cdk

import constants
from deployment import AwsSkillsMapping
from deployment import AwsSkillsMappingPipeline
from environment import AwsSkillsMappingConfigDev
from environment import AwsSkillsMappingConfigPreProd
from environment import PipelineConfig

# from pipeline_app import AwsSkillsMappingPipelineProps

# from pipeline import Pipeline

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
pipeline_config = PipelineConfig()
app_pipeline = AwsSkillsMappingPipeline(
    app,
    "AwsSkillsMapping-PIPELINE",
    pipe_config=pipeline_config,
    env=pipeline_config.env,
)
app_pipeline.add_deploy_stage(dev_stage)
app_pipeline.add_approval_stage()
app_pipeline.add_deploy_stage(preprod_stage)


# # PRE-PRODUCTION and PRODUCTION Stage will be deployed using this Pipeline
# # Our Pipeline application will create the infra for CodePipeline and CodeBuild
# pip = PipelineProps()
# Pipeline(
#     app,
#     f"{constants.CDK_APP_NAME}-Pipeline",
#     env=pip.env,  # We will deploy the Pipeline in Development Environment
# )

app.synth()
