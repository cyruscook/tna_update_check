#!/bin/sh

set -ex
cd "$(dirname "$0")"

rm -f lambda.zip

uv export --frozen --no-dev --no-editable -o requirements.txt
uv pip install \
   --no-installer-metadata \
   --no-compile-bytecode \
   --python-platform aarch64-manylinux2014 \
   --python 3.13 \
   --target packages \
   -r requirements.txt

cd packages
zip -r ../lambda.zip .
cd ..

cd src
zip -r ../lambda.zip .
cd ..
