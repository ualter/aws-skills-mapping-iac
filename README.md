
# **AWS Skills Mapping IaC** - *AWS-CDK Python*

**AWS Skills Mapping IaC** is an AWS CDK Python project, aiming to build the infrastructure environment ( ***[IaC](https://en.wikipedia.org/wiki/Infrastructure_as_code)*** ) required by the application [AWS Skills Mapping](https://github.com/ualter/aws-skills-mapping-app).

Actually, its main purpose is to serve as a ***sandbox*** project...  i.e. a sample (**Blueprint**) and guide to organize, to structure, to apply (*good / best*) practices, and patterns in the development of Cloud Solutions using AWS CDK.

---

### **Structure**
```bash
CDK-Proj-Repo
 |
 ├── website                 # <---- Logical Unit and its infrastructure
 │   └── infrastructure.py
 |
 ├── api                     # <---- Logical Unit and its infrastructure
 │   ├── infrastructure.py
 │   └── runtime             # <---- Runtime assets (Lambda function code)
 │       └── index.js
 |
 ├── database                # <---- Logical Unit and its infrastructure
 │   └── infrastructure.py
 │       
 |
 ├── deployment.py           # <---- Modeling your Application, its Stages and Stacks(unit of deployments)
 ├── environment.py          # <---- Environments and Stage Configurations information
 ├── app.py                  # <---- Instantiate an Application (Stage) and deploy it
 |                           #       in an environment with a specific desired loaded configuration. 
 |                           #       (Instantiate it multiple times to deploy in more than one environment/stage)
 ├── pipeline.py             # <---- Create an AWS Pipeline and CodeBuild (self-mutating) for the Application IaC deployment (Optional)
 └── constants.py            # <---- Well, you know...

```

#### **Logical Units**
The logical unit consist of [Constructs](https://docs.aws.amazon.com/cdk/api/v2/python/constructs.html), not [Stacks](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk/Stack.html). Each logical unit will include the related infrastructure (e.g., Amazon S3 buckets, Amazon RDS databases, Amazon VPC network), runtime (e.g., AWS Lambda function code), and configuration code.

---

### **Quick Start**

0. [**Before start...**](#my-platform---aws-cdk-python-project-blueprint)

- Create a secret at [AWS Secrets Manager](https://aws.amazon.com/es/secrets-manager/) with a valid [Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) to Application's Github repository. The Pipeline created in this IaC solution will need that information. It must be created in the same AWS Region where the Pipeline (`AWS CodePipeline, CodeBuild`) is deployed (*remember to grant access for repo_hooks*).

`$ aws secretsmanager create-secret --region=eu-west-3 --name=github-ualter --description="My github token" --secret-string="[YOUR-PERSONAL-ACCESS-TOKEN-HERE]"`
  
- Verify and complete with your application configuration correct values (`Account, Region, Bucket-Prefix, Repository, etc...`) in the files located at `configuration` folder.
```bash
./configuration
  |
  ├── environments            # <---- Configuration values (different) for each 
  │   ├── dev.yml             #       environment and the Application Pipeline
  │   ├── preprod.yml
  │   ├── pipeline.yml
  │   └── ...
  └── default.yml             # <---- Default values (equal for all environments)

```

```bash
$ source ./scripts/set-env.sh
$ python -m venv .venv
$ source .venv/bin/activate
$ python -m pip install pip-tools
$ pip-compile requirements.in
$ pip-compile requirements-dev.in
# install dependencies
./scripts/install-deps.sh  # check/change cdk version at package.json
./scripts/run-checks.sh
# and wait with a...
     )  ( 
     (   ) )
      ) ( (
    _(_____)_
 .-'---------|  
( C|/\/\/\/\/|
 '-./\/\/\/\/|
   '_________'
    '-------' 
# check installed dependencies
pip list

# Troubleshooting: (Error "Role XXX not authorized to perform: cloudformation:GetTemplate")
# Add this like to cdk.json (a feature flag)
"@aws-cdk/core:newStyleStackSynthesis": true,
```
1. [**Bootstrapping**](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)
```bash

#
# In case of using the makefile targets below to boostrap AWS Environments (account/region), 
# they make use of Environment Variables (ex: CDK_DEVELOPMENT_ACCOUNT, CDK_DEVELOPMENT_REGION) to perform their functions, 
# take a look at the file ./scripts/set-env-template.sh to help set this required env vars for the scripts.
#
$ make bootstrap-dev    # development 
$ make bootstrap-pre    # pre-production
$ make bootstrap-prod   # production
$ make bootstrap-pip    # pipeline
$ make check-bootstrap  # check status of all
```
2. [**Synthesize**](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)
```bash
$ make synth
```
2. [**Deploy**](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)
```bash
$ make deploy
```

**Check more actions at makefile**
```bash
make help
```

---



#### **What ?**
* **Constructs**
  * Basic building block of AWS CDK Application. Check `class BucketStaticWebSiteHosting(cdk.Construct)` at file `./s3/infrastructure.py`.
* **Stacks**
  * Deployment units. All AWS Resources defined in a stack are provisioned as a single unit. (fail or work together). Check `class AwsSkillsMapping(cdk.Stage)` at file `deployment.py`, there the Stacks are being defined. Here, we split in two:
    *  Stateful (database, s3)
    *  Stateless (api, sns, mq)

---

#### **Cheat Sheet / Extra Info**

Just some annotations, to help remember something quickly.
```bash

# --------------------------------------
# Starting new app (template / skeleton)
# --------------------------------------
cdk init app --language python


# ----------------------------
# List CodeBuild Docker Images
# ----------------------------
aws codebuild list-curated-environment-images
# Images (DockerFile) https://github.com/aws/aws-codebuild-docker-images/


# -----------------------------------------------
# Run builds locally with the AWS CodeBuild agent
# -----------------------------------------------
# https://docs.aws.amazon.com/codebuild/latest/userguide/use-codebuild-agent.html
# 1. Pull it from the CodeBuild public Amazon ECR repository... 
docker pull public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:3.0
# 1. or... clone the CodeBuild image repo:
git clone https://github.com/aws/aws-codebuild-docker-images.git
##   Change to the image directory
     cd aws-codebuild-docker-images/ubuntu/standard/5.0
##   Build the image
     docker build -t aws/codebuild/standard:5.0 .
# 2. Download the  x86_64 version of the agent
docker pull public.ecr.aws/codebuild/local-builds:latest
# 3. Run the CodeBuild agent, change to the directory that contains your build project source
wget https://raw.githubusercontent.com/aws/aws-codebuild-docker-images/master/local_builds/codebuild_build.sh
chmod +x codebuild_build.sh
# 4. Run the codebuild_build.sh script and specify your container image and the output directory
#        to specify the location of the build project, add the -s <build project directory>
./codebuild_build.sh -i aws/codebuild/standard:5.0 -a /tmp/artifact -s ./ -b ./codebuild/buildspec.yml

```

#### **Troubleshootings**
- **mypy checking errors**
  - *Error*: 
    - `error: Library stubs not installed for "yaml" (or incompatible with Python 3.8)  [import]`
  - *Solution*: 
    - `python3 -m pip install types-PyYAML`

#### **Links**
 - AWS CDK Toolkit (cdk command): https://docs.aws.amazon.com/cdk/v2/guide/cli.html

