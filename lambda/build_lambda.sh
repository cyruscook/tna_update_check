#!/bin/sh

set -ex
cd "$(dirname "$0")"

rm -f lambda.zip

mkdir -p py_deps
cd py_deps
pip install --platform manylinux2014_aarch64 --implementation cp --python-version 3.13 --only-binary=:all: --upgrade --target . -r ../requirements.txt
zip -r ../lambda.zip ./**
cd ..
rm -rf py_deps

cd src
zip -r ../lambda.zip ./**
cd ..
