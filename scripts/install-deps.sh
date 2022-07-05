#!/bin/bash

set -o errexit
set -o verbose

if [[ "$VIRTUAL_ENV" != "" ]]
then
  INVENV=1
else
  INVENV=0
fi

if [[ "$INVENV" == "0" ]]; then
    clear
    printf "\n"
    printf " \033[36m--> Ops! No Virtual Environment activated!\n"
    printf " \033[36mPlease, run: \033[33msource .venv/bin/activate\033[36m, before install dependencies\033[0m\n"
    exit
fi

# # Install local CDK CLI version
# npm install

# # Install project dependencies
pip install -r requirements.txt -r requirements-dev.txt
