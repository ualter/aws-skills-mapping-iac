#!/usr/bin/env python3
from aws_cdk import core as cdk

import constants
from deployment import AwsSkillsMapping
from environment import AwsSkillsMappingPropsDev

# from pipeline import Pipeline

app = cdk.App()

# DEVELOPMENT Stage
dev = AwsSkillsMappingPropsDev()
AwsSkillsMapping(
    app,
    f"{constants.CDK_APP_NAME}-Dev",
    props=dev,
    env=dev.env,
)

# # PRE-PRODUCTION and PRODUCTION Stage will be deployed using this Pipeline
# # Our Pipeline application will create the infra for CodePipeline and CodeBuild
# pip = PipelineProps()
# Pipeline(
#     app,
#     f"{constants.CDK_APP_NAME}-Pipeline",
#     env=pip.env,  # We will deploy the Pipeline in Development Environment
# )

app.synth()
