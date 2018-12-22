#!/bin/bash

set -e

SOURCE_BRANCH="master"
TARGET_BRANCH="gh-pages"

REPO=`git config remote.origin.url`
SSH_REPO=${REPO/https:\/\/github.com\//git@github.com:}
SHA=`git rev-parse --verify HEAD`

rm -rf .git
cd docs
bundle install
bundle exec jekyll b --future
cd _site
git init
git remote add origin $SSH_REPO
git checkout --orphan gh-pages

git config user.name "Travis, CI"
git config user.email "travis-ci@ucfsigai.org"

git add .
git commit -m "Deploying ${SHA} to GitHub Pages"

cp ../../dsg.ucfsigai.org.enc .
ENCRYPTED_KEY_VAR="encrypted_${ENCRYPTION_LABEL}_key"
ENCRYPTED_IV_VAR="encrypted_${ENCRYPTION_LABEL}_iv"
ENCRYPTED_KEY=${!ENCRYPTED_KEY_VAR}
ENCRYPTED_IV=${!ENCRYPTED_IV_VAR}
openssl aes-256-cbc -K $ENCRYPTED_KEY -iv $ENCRYPTED_IV -in dsg.ucfsigai.org.enc -out dsg.ucfsigai.org -d
chmod 600 dsg.ucfsigai.org
eval `ssh-agent -s`
ssh-add deploy_key

rm dsg.ucfsigai.org dsg.ucfsigai.org.enc

git push --force origin $TARGET_BRANCH