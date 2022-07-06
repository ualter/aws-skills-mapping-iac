#!/bin/bash

alias mk='make $1 $2 $3 $4 $5 $6 $7'

export CDK_GITHUB_CONNECTION_ARN="arn:aws:codestar-connections:region:XXXXXXXXXXX:connection/YYYYYYYYYYYYYYYYYYYYYY"
export CDK_GITHUB_OWNER="ualter"
export CDK_GITHUB_REPO="repo-name"
export CDK_GITHUB_TRUNK_BRANCH="v0.0.0"

export CDK_DEVELOPMENT_ACCOUNT=1111111
export CDK_DEVELOPMENT_REGION=us-xxx-2

export CDK_PREPROD_ACCOUNT=123456
export CDK_PREPROD_REGION=eu-xxx-1

export CDK_NEW_BOOTSTRAP=1 # Set this to bootstrap an environment that can provision an AWS CDK pipeline
export CDK_PIPELINE_ACCOUNT=11111111
export CDK_PIPELINE_REGION=us-xxx-2

export CDK_PRODUCTION_ACCOUNT=11111111
export CDK_PRODUCTION_REGION=eu-xxx-2

export CDK_BOOTSTRAP_ACCOUNT=111111111
export CDK_BOOTSTRAP_REGION=eu-xxx-2
