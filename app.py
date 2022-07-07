#!/usr/bin/env python3
from aws_cdk import core as cdk

import constants
from deployment import AwsSkillsMapping
from environment import AwsSkillsMappingPropsDev
from environment import AwsSkillsMappingPropsPreProd
from environment import PipelineProps
from pipeline_app import AwsSkillsMappingPipeline

# from pipeline_app import AwsSkillsMappingPipelineProps

# from pipeline import Pipeline

app = cdk.App()

# IaC DEVELOPMENT Stage
dev_props = AwsSkillsMappingPropsDev()
dev_stage = AwsSkillsMapping(
    app,
    f"{constants.CDK_APP_NAME}-{dev_props.stage_name().upper()}",
    props=dev_props,
    env=dev_props.env,
)

# IaC PREPROD Stage
preprod_props = AwsSkillsMappingPropsPreProd()
preprod_stage = AwsSkillsMapping(
    app,
    f"{constants.CDK_APP_NAME}-{preprod_props.stage_name().upper()}",
    props=preprod_props,
    env=preprod_props.env,
)

# PIPELINE Application: aws-skills-mapping
app_pipeline = AwsSkillsMappingPipeline(
    app, "AwsSkillsMapping-PIPELINE", env=PipelineProps().env
)
app_pipeline.add_deploy_stage(dev_stage)
# app_pipeline.add_approval_stage()
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
