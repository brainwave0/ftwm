#!/bin/bash
set -e

commit_message=$1

autopep8 --in-place --recursive .
mypy --strict src
tox

echo The following changes will be committed:
git status
read -p "Is this okay? (y/n): "
if [[ $REPLY != "y" ]]; then exit 1; fi
git add .

git commit -m "$commit_message"
git push
