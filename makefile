.DEFAULT_GOAL := help
SHELL = /usr/bin/env bash -o pipefail
.SHELLFLAGS = -ec

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-18s\033[33m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ --| AWS-CDK   |--------------------------------------------------------------------------------------------------------------------------------------

bootstrap-dev: check-tools ## cdk bootstrap-dev (development)
	$(MAKE) -s exec-bootstrap-dev

bootstrap-pre: check-tools ## cdk bootstrap-pre (Pre-Production)
	$(MAKE) -s exec-bootstrap-pre

bootstrap-pip: check-tools ## cdk bootstrap-pip (CDK Pipelines)
	$(MAKE) -s exec-bootstrap-pip

bootstrap-prod: check-tools ## cdk bootstrap-prod (production)
	$(MAKE) -s exec-bootstrap-prod

## (INTERNAL)
exec-bootstrap-%:
	clear ; \
	$(MAKE) -s check-boot-envvars; \
	printf " \n"; \
	if [[ "$*" == "dev" ]]; then \
	    export stage_name="DEVELOPMENT"; \
		export stage_nickname="dev"; \
		export size=6; \
		export stage_acc=${CDK_DEVELOPMENT_ACCOUNT}; \
		export stage_region=${CDK_DEVELOPMENT_REGION}; \
	elif [[ "$*" == "pre" ]]; then \
		export stage_name="PRE-PRODUCTION"; \
		export stage_nickname="pprod"; \
		export size=4; \
		export stage_acc=${CDK_PREPROD_ACCOUNT}; \
		export stage_region=${CDK_PREPROD_REGION}; \
	elif [[ "$*" == "prod" ]]; then \
		export stage_name="PRODUCTION"; \
		export stage_nickname="prod"; \
		export size=5; \
		export stage_acc=${CDK_PRODUCTION_ACCOUNT}; \
		export stage_region=${CDK_PRODUCTION_REGION}; \
	elif [[ "$*" == "pip" ]]; then \
		export stage_name="PIPELINE"; \
		export stage_nickname="pipe"; \
		export size=5; \
		export stage_acc=${CDK_PIPELINE_ACCOUNT}; \
		export stage_region=${CDK_PIPELINE_REGION}; \
	fi; \
	$(call generate_random,$$size,"$$stage_nickname-"); \
	printf " \033[36m Stage...................: \033[33m$$stage_name \033[0m\n"; \
	# printf " \033[36m Qualifier...............: \033[33m$$TMP_RND \033[0m\n"; \
	printf " \033[36m Termination Protection..: \033[33mfalse \033[0m\n"; \
	printf " \n"; \
	# cdk bootstrap --qualifier $$TMP_RND --termination-protection=false aws://$$stage_acc/$$stage_region; \
	# cdk bootstrap --stack-name CDKToolkit --termination-protection=false aws://$$stage_acc/$$stage_region; \
	cdk bootstrap --termination-protection=false aws://$$stage_acc/$$stage_region; \
	printf " \033[36m---------------------------------------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (Bootstraped \033[33m$$stage_name\033[36m aws://\033[33m$$stage_acc\033[36m/\033[33m$$stage_region\033[36m)\033[0m\n"; \
	printf " \033[36m---------------------------------------------------------------------------\033[0m\n"; \
	printf " \n"; \

## (I am not sure...)
# bootstrap-dev-chk: check-tools ## check bootstrap state in development
# 	$(MAKE) -s chk-bootstrap-dev

# bootstrap-pre-chk: check-tools ## check bootstrap state in pre-production
# 	$(MAKE) -s chk-bootstrap-pre

# bootstrap-prod-chk: check-tools ## check bootstrap state in production
# 	$(MAKE) -s chk-bootstrap-prod

# bootstrap-pip-chk: check-tools ## check bootstrap state in pipeline
# 	$(MAKE) -s chk-bootstrap-pip

## (INTERNAL)
chk-bootstrap-%: 
	$(MAKE) -s check-boot-envvars; \
	printf " \n"; \
	if [[ "$*" == "dev" ]]; then \
	    export stage_name="DEVELOPMENT"; \
		export stage_region=${CDK_DEVELOPMENT_REGION}; \
	elif [[ "$*" == "pre" ]]; then \
		export stage_name="PRE-PRODUCTION"; \
		export stage_region=${CDK_PREPROD_REGION}; \
	elif [[ "$*" == "prod" ]]; then \
		export stage_name="PRODUCTION"; \
		export stage_region=${CDK_PRODUCTION_REGION}; \
	elif [[ "$*" == "pip" ]]; then \
		export stage_name="PIPELINE"; \
		export stage_region=${CDK_PIPELINE_REGION}; \
	fi; \
	source ./scripts/makefile-scripts.sh CHECK_BOOTSTRAP $$stage_region; \
	export check_result=$${RESULT}; \
	if [ "$${check_result}" = "" ]; then \
		printf " \033[0;91m  KO! \033[36m--> \033[36m$$stage_name (\033[0;91mNOT Bootstraped\33[36m)\n"; \
	else \
	    printf " \033[33m  OK!\033[36m --> \033[36m$$stage_name\n   Stack ARN: \033[33m$${check_result}\n"; \
	fi; \
	printf " \033[0m"; \

.SILENT: check-bootstrap
check-bootstrap: check-tools ## Check bootstrap status of all environments
	@clear; \
	$(MAKE) -s chk-bootstrap-dev
	$(MAKE) -s chk-bootstrap-pre
	$(MAKE) -s chk-bootstrap-prod
	$(MAKE) -s chk-bootstrap-pip
	printf "\n"

ls: check-tools ## cdk ls
	@printf " \n"; \
	# $(MAKE) -s check-envvars; \
	cdk ls ; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (ls)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

synth: check-tools ## cdk synth, syntax: make diff stacks="AwsSkillsMapping-DEV/*,AwsSkillsMapping-PREPROD/*"
	clear ; \
	printf " \n"; \
	if [ "${stacks}" = "" ]; then \
		source ./scripts/makefile-scripts.sh CHOOSE_STACK Synth; \
		printf " \033[36m  Chosen: \033[33m$${RESULT}\n\n"; \
		export stacks=$${RESULT}; \
	else \
	    export stacks=${stacks}; \
	fi; \
	cdk synth $${stacks//,/ }; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (synth)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

# make diff stacks="AwsSkillsMapping-Dev/*"
# make diff
diff: check-tools ## cdk diff, syntax: make diff stacks="AwsSkillsMapping-DEV/*,AwsSkillsMapping-PREPROD/*"
	clear ; \
	printf " \n"; \
	if [ "${stacks}" = "" ]; then \
		source ./scripts/makefile-scripts.sh CHOOSE_STACK Diff; \
		printf " \033[36m  Chosen: \033[33m$${RESULT}\n\n"; \
		export stacks=$${RESULT}; \
	else \
	    export stacks=${stacks}; \
	fi; \
	cdk diff $${stacks//,/ }; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (diff)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

ls-diffs: check-tools ## List all Pipelines, marking those with diffs found
	clear ; \
	printf " \n"; \
	source ./scripts/makefile-scripts.sh LIST_DIFFS Synth; \
	printf " \n"; \

deploy: check-tools ## cdk deploy, syntax: make diff stacks="AwsSkillsMapping-DEV/*,AwsSkillsMapping-PREPROD/*"
	clear ; \
	printf " \n"; \
	if [ "${stacks}" = "" ]; then \
		source ./scripts/makefile-scripts.sh CHOOSE_STACK Deploy; \
		printf " \033[36m  Chosen: \033[33m$${RESULT}\n\n"; \
		export stacks=$${RESULT}; \
	else \
	    export stacks=${stacks}; \
	fi; \
	printf " \033[36m ==> Deploying...: \033[33m$${stacks//,/ }\033[0m\n"; \
	cdk deploy $${stacks//,/ } --progress=bar --require-approval never; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (deploy)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

destroy: check-tools ## cdk destroy --force, syntax: make destroy stacks="AwsSkillsMapping-DEV/*,AwsSkillsMapping-PREPROD/*"
	clear ; \
	printf " \n"; \
	if [ "${stacks}" = "" ]; then \
		source ./scripts/makefile-scripts.sh CHOOSE_STACK Destroy; \
		printf " \033[36m  Chosen: \033[33m$${RESULT}\n\n"; \
		export stacks=$${RESULT}; \
	else \
	    export stacks=${stacks}; \
	fi; \
	printf " \033[36m ==> Destroying...: \033[33m$${stacks//,/ }\033[0m\n"; \
	cdk destroy $${stacks//,/ } --force; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (destroy)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

deploy-all: check-tools ## cdk deploy, sequence: 1º("AwsSkillsMapping-DEV/*" "AwsSkillsMapping-PREPROD/*"), then 2º("AwsSkillsMapping-PIPELINE")
	clear ; \
	printf " \n"; \
	printf " \033[36m ==> Deploying...\033[0m\n"; \
	printf " \033[36m     (1) \033[33mAwsSkillsMapping-DEV/*\033[0m\n"; \
	printf " \033[36m     (1) \033[33mAwsSkillsMapping-PREPROD/*\033[0m\n"; \
	printf " \033[36m     (2) \033[33mAwsSkillsMapping-PIPELINE\033[0m\n"; \
	cdk deploy "AwsSkillsMapping-DEV/*" "AwsSkillsMapping-PREPROD/*" --progress=bar --require-approval never; \
	cdk deploy "AwsSkillsMapping-PIPELINE" --progress=bar --require-approval never; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (deploy-all)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

destroy-all: check-tools ## cdk destroy --force, sequence: 1º("AwsSkillsMapping-PIPELINE"), then 2º("AwsSkillsMapping-DEV/*" "AwsSkillsMapping-PREPROD/*")
	clear ; \
	printf " \n"; \
	printf " \033[36m ==> Destroying...\033[0m\n"; \
	printf " \033[36m     (1) \033[33mAwsSkillsMapping-PIPELINE\033[0m\n"; \
	printf " \033[36m     (2) \033[33mAwsSkillsMapping-DEV/*\033[0m\n"; \
	printf " \033[36m     (2) \033[33mAwsSkillsMapping-PREPROD/*\033[0m\n"; \
	cdk destroy --force "AwsSkillsMapping-PIPELINE"; \
	cdk destroy --force "AwsSkillsMapping-DEV/*" "AwsSkillsMapping-PREPROD/*"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (destroy-all)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

docs: check-tools ## cdk docs
	@printf " \n"; \
	cdk docs ; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (docs)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

version: check-tools ## cdk version
	@printf " \n"; \
	cdk version ; \
	printf " \n"; \


##@ --| Python    |--------------------------------------------------------------------------------------------------------------------------------------

pytest: check-tools ## Run pytest
	clear ; \
	printf " \n"; \
	pytest -sv ; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (pytest)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \


venv-on: check-tools ## Start .venv Python Virtual Environment
	@printf " \n"; \
	printf " \033[36mrun: \033[33msource .venv/bin/activate\033[0m\n"; \
	printf " \n"; \

venv-off: check-tools ## Leave .venv Python Virtual Environment
	@printf " \n"; \
	printf " \033[36mrun: \033[33mdeactivate\033[0m\n"; \
	printf " \n"; \

##@ --| AWS       |--------------------------------------------------------------------------------------------------------------------------------------

whoiam: check-tools ## Check my current identity (aws sts get-caller-identity)
	clear ; \
	printf " \n"; \
	aws sts get-caller-identity; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (activate)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

##@ --| Utils     |--------------------------------------------------------------------------------------------------------------------------------------

chk-code:  ## Code checking with python tools: quality, format, security
	clear ; \
	./scripts/run-checks.sh ; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (checks)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

chk-code-act:  ## Code checking and perform actions (if needed), python tools
	clear ; \
	./scripts/run-checks.sh perform-actions; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (checks)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

show-envs:  ## Show my environments (CDK Dev, PreProd, Prod Account/Region)
	@printf " \n\033[33m ENVIRONMENTS (Account/Region)\n"; \
	printf " \033[36m-------------------------------------------------\n"; \
	printf " \033[36mDevelopment....: \033[33m${CDK_DEVELOPMENT_ACCOUNT}/${CDK_DEVELOPMENT_REGION}\033[0m\n"; \
	printf " \033[36mPre-Production.: \033[33m${CDK_PREPROD_ACCOUNT}/${CDK_PREPROD_REGION}\033[0m\n"; \
	printf " \033[36mProduction.....: \033[33m${CDK_PRODUCTION_ACCOUNT}/${CDK_PRODUCTION_REGION}\033[0m\n"; \
	printf " \033[36mPipeline.......: \033[33m${CDK_PIPELINE_ACCOUNT}/${CDK_PIPELINE_REGION}\033[0m\n"; \
	printf " \n\033[33m GITHUB (Account/Region)\n"; \
	printf " \033[36m-------------------------------------------------\n"; \
	printf " \033[36mARN Connection..: \033[33m${CDK_GITHUB_CONNECTION_ARN}\033[0m\n"; \
	printf " \033[36mOwner...........: \033[33m${CDK_GITHUB_OWNER}\033[0m\n"; \
	printf " \033[36mRepository......: \033[33m${CDK_GITHUB_REPO}\033[0m\n"; \
	printf " \033[36mTrunk\Branch....: \033[33m${CDK_GITHUB_TRUNK_BRANCH}\033[0m\n\n"; \
	printf " \n"; \

show-config: ## Show my configurations from YAML files
	@printf " \n\033[33m CONFIGURATIONS (./configuration/**/*.yml)\n"; \
	python configuration.py ; \

codebuild-build: ## Run builds locally with the AWS CodeBuild agent (check README for installation)
	clear ; \
	export file_env=./codebuild/codebuild.env; \
	printf "\n \033[36m------------------------------------------------------------------------\033[0m\n"; \
	printf " \033[33m Running \033[36mCodeBuild\033[33m buildings locally...\033[0m\n"; \
	printf " \033[33m --> Environment Variables from file: \033[36m$$file_env\033[0m\n"; \
	printf " \033[36m------------------------------------------------------------------------\033[0m\n\n"; \
	if [ ! -f "$$file_env" ]; then \
		printf " \033[36m----------------------------------------------------------------------------------------\033[0m\n"; \
		printf " \033[33m The file \033[34m$$file_env \033[33mneeds to be defined with the Environment Variables\033[0m\n"; \
		printf " \033[33m Must have the \033[34mEnvironment Variables\033[33m (\033[35mVAR=VALUE\033[33m) for CodeBuild buildings\033[0m\n"; \
		printf " \033[36m----------------------------------------------------------------------------------------\033[0m\n\n"; \
		exit 1; \
	fi; \
	./codebuild_build.sh -e $$file_env -i aws/codebuild/standard:5.0 -a /tmp/artifact -s ./ -b ./codebuild/buildspec.yml; \
	printf "\n \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (codebuild-build)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

install-deps:  ## Install Python dependencies (dev and runtime)
	clear ; \
	pip-compile requirements.in ; \
	pip-compile requirements-dev.in ; \
	./scripts/install-deps.sh; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \033[36mDone! (install deps)\033[0m\n"; \
	printf " \033[36m-------------------------------------------\033[0m\n"; \
	printf " \n"; \

check-tools: # Check if the necessary tools are installed
ifneq (,$(which cdk))
	$(error "AWS-CDK not installed!")
endif
ifneq (,$(which npm))
	$(error "NPM not installed!")
endif
ifneq (,$(which python))
	$(error "Python not installed!")
endif


## (INTERNAL) Check if the necessary environment variable are set
check-var-stacks:
	@ if [ "${STACKS}" = "" ]; then \
		printf "\n"; \
		printf " \033[36m---------------------------------------------------------------\033[0m\n"; \
		printf " \033[36m Parameter STACKS not informed \033[33m$*\033[36m not set\033[0m\n"; \
		printf " \033[36m---------------------------------------------------------------\033[0m\n"; \
		printf "\n"; \
		exit 1; \
	fi

## (INTERNAL) Check if the necessary environment variable are set
check-envvars: 
	$(MAKE) -s envvar-CDK_DEVELOPMENT_ACCOUNT; \
	$(MAKE) -s envvar-CDK_DEVELOPMENT_REGION; \
	$(MAKE) -s envvar-CDK_PREPROD_ACCOUNT; \
	$(MAKE) -s envvar-CDK_PREPROD_REGION; \
	$(MAKE) -s envvar-CDK_PIPELINE_ACCOUNT; \
	$(MAKE) -s envvar-CDK_PIPELINE_REGION; \
	$(MAKE) -s envvar-CDK_PRODUCTION_ACCOUNT; \
	$(MAKE) -s envvar-CDK_PRODUCTION_REGION; \
	$(MAKE) -s envvar-VIRTUAL_ENV; \

## (INTERNAL) Check if the necessary environment variable for bootstrap are set
check-boot-envvars: 
	$(MAKE) -s envvar-CDK_BOOTSTRAP_ACCOUNT; \
	$(MAKE) -s envvar-CDK_BOOTSTRAP_REGION; \

## (INTERNAL) Check if the environment variable is set
envvar-%: 
	@ if [ "${${*}}" = "" ]; then \
	    if [[ "$*" == "VIRTUAL_ENV" ]]; then \
			printf "\n"; \
			printf " \033[36m---------------------------------------------------------------\033[0m\n"; \
			printf " \033[36m Python Virtual Environment \033[37mNOT \033[33mactivated\033[0m\n"; \
			printf " \033[36m Run: \033[33msource .venv/bin/activate\033[0m\n"; \
			printf " \033[36m---------------------------------------------------------------\033[0m\n"; \
			printf "\n"; \
		else \
			printf "\n"; \
			printf " \033[36m---------------------------------------------------------------\033[0m\n"; \
			printf " \033[36m Environment variable \033[33m$*\033[36m not set\033[0m\n"; \
			printf " \033[37m Run: \033[33msource ./scripts/set-env.sh\033[0m\n"; \
			printf " \033[36m---------------------------------------------------------------\033[0m\n"; \
			printf "\n"; \
		fi; \
		exit 1; \
    fi

define generate_random
{ \
set -e ; \
TMP_RND="$(2)$$(tr -dc a-z0-9 </dev/urandom  | head -c $(1) ; echo '')" ; \
}
endef

test:
	clear; \
	export stage_nickname="prod"; \
	export size=5; \
	$(call generate_random,$$size,$$stage_nickname-); \
	printf "$$TMP_RND \n"





