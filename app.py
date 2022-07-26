#!/usr/bin/env python3
from aws_cdk import core as cdk

import constants
from deployment import AwsSkillsMapping
from deployment import AwsSkillsMappingPipeline
from environment import AwsSkillsMappingConfigDev
from environment import AwsSkillsMappingConfigPipeline
from environment import AwsSkillsMappingConfigPreProd

# from aws_cdk import custom_resources as cr


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
app_pipeline = AwsSkillsMappingPipeline(
    app,
    f"{constants.CDK_APP_NAME}-PIPELINE",
    pipe_config=pipeline_config,
    env=pipeline_config.env,
)

app_pipeline.add_deploy_stage(dev_stage, dev_config)
app_pipeline.add_approval_stage()
app_pipeline.add_deploy_stage(preprod_stage, preprod_config)


########################################################################################################################
# NOTICE!
#   As we are using a S3 Static Website to host our Angular sample project,
#   we do not have the option of "inject" Environment Variables to be used during Runtime, because...
#   S3 is a static object store, not a dynamic content server, so there's now such a thing like "Runtime",
#   This is the reason, of why we have to have a Build Stage for each environment, to setup different variable values
#   by each environment, we have to configured them at "Buildtime".
########################################################################################################################


# # PRE-PRODUCTION and PRODUCTION Stage will be deployed using this Pipeline
# # Our Pipeline application will create the infra for CodePipeline and CodeBuild
# pip = PipelineProps()
# Pipeline(
#     app,
#     f"{constants.CDK_APP_NAME}-Pipeline",
#     env=pip.env,  # We will deploy the Pipeline in Development Environment
# )

app.synth()
