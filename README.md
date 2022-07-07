
# **AWS Skills Mapping IaC** - *AWS-CDK Python*

**AWS Skills Mapping IaC** is a AWS CDK Python project, aiming to build the infrastructure environment ( ***[IaC](https://en.wikipedia.org/wiki/Infrastructure_as_code)*** ) required by the application [AWS Skills Mapping](https://github.com/ualter/aws-skills-mapping-app).

Actually, its main purpose is to serve as a ***sandbox*** project...  i.e. a sample (**Blueprint**) and guide to organize, to structure, to apply (*good / best*) practices, and patterns in the development of Cloud Solutions using AWS CDK.

---

### **Structure**
```bash
Github-Repo
|
├── s3                      # <---- Logical Unit and its infrastructure
│   └── infrastructure.py
|
├── api                     # <---- Logical Unit and its infrastructure
│   ├── infrastructure.py
│   └── runtime             # <---- Runtime assets (Lambda function code)
│       └── app.js
|
├── database                # <---- Logical Unit and its infrastructure
│   └── infrastructure.py
│       
|
├── deployment.py           # <---- Modeling your Application and its Stacks
├── environment.py          # <---- Stages, Environments and Properties of your Application
├── app.py                  # <---- Instantiate the Application and deploy 
|                           #       in a environment. Instantiate it multiple 
|                           #       times to deploy in more than one environment
├── pipeline.py             # <---- Create an AWS Pipeline and CodeBuild for Production stage deploy
└── constants.py            # <---- Well, you know... :-)

```

#### **Logical Units**
The logical unit consist of [Constructs](https://docs.aws.amazon.com/cdk/api/v2/python/constructs.html), not [Stacks](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk/Stack.html). Each logical unit will include the related infrastructure (e.g., Amazon S3 buckets, Amazon RDS databases, Amazon VPC network), runtime (e.g., AWS Lambda function code), and configuration code.

---

### **Quick Start**

0. [**Before start...**](#my-platform---aws-cdk-python-project-blueprint)

Set the Environment Variables (AWS ACCOUNT and REGION) for bootstrapping and the target Cloud environment (Account/Region). *Notice! Create the file `./scripts/set-env.sh`, copying the template `./scripts/set-env-template.sh`, and replace for real values.*
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
  * Basic building block of AWS CDK Application. Check `class BucketHelmRepo(cdk.Construct)` at file `./s3/infrastructure.py`.
* **Stacks**
  * Deployment units. All AWS Resources defined in a stack are provisioned as a single unit. (fail or work together). Check `class MyPlatform(cdk.Stage)` at file `deployment.py`, there the Stacks are being defined. Here, we split in two:
    *  Stateful (database, s3)
    *  Stateless (api, sns, mq)

---

#### **Cheat Sheet / Extra Info**
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

#### **Links**
 - AWS CDK Toolkit (cdk command): https://docs.aws.amazon.com/cdk/v2/guide/cli.html

