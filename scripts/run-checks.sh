#!/bin/bash

set -o errexit
# set -o verbose

# targets=(api database monitoring tests app.py constants.py deployment.py pipeline.py)
targets=(website database api app.py deployment.py environment.py constants.py repository.py custom_resources.py)

CHECK_PARAMS="--check --diff"
if [ "$1" == "perform-actions" ]; then
   CHECK_PARAMS=""
fi

# Find common security issues (https://bandit.readthedocs.io)
bandit --recursive "${targets[@]}"

# Python code formatter (https://black.readthedocs.io)
black $CHECK_PARAMS "${targets[@]}"

# Style guide enforcement (https://flake8.pycqa.org)
flake8 --config .flake8 "${targets[@]}"

# Sort imports (https://pycqa.github.io/isort)
isort --settings-path .isort.cfg $CHECK_PARAMS "${targets[@]}"

# Static type checker (https://mypy.readthedocs.io)
# Split commands due to https://github.com/python/mypy/issues/4008
# mypy --config-file .mypy.ini "${targets[@]:0:4}"
# mypy --config-file .mypy.ini "${targets[@]:4}"
mypy --no-warn-unused-ignores --show-error-codes --config-file  .mypy.ini "${targets[@]}"

# Check for errors, enforce a coding standard, look for code smells (http://pylint.pycqa.org)
# pylint --rcfile .pylintrc "${targets[@]}"

# Check dependencies for security issues (https://pyup.io/safety)
# Ignore coverage 5.5 (41002) report, no issues per Snyk: https://snyk.io/vuln/pip:coverage@5.5
safety check \
  -i 41002 \
  -r requirements.txt \
  -r requirements-dev.txt

# Report code complexity (https://radon.readthedocs.io)
radon mi "${targets[@]}"

# Exit with non-zero status if code complexity exceeds thresholds (https://xenon.readthedocs.io)
xenon --max-absolute A --max-modules A --max-average A "${targets[@]}"

# Run tests and measure code coverage (https://coverage.readthedocs.io)
# PYTHONPATH="${PWD}/api/runtime" \
#   coverage run --source "${PWD}" --omit ".venv/*,tests/*" -m unittest discover -v -s tests
