#!/bin/bash

# Prepare script for the akkaserverless-javascript-sdk package

# Delete and recreate the proto directory
rm -rf ./proto
mkdir -p ./proto

# get the framework version from settings.js
readonly framework_version="0.7.0-beta.14"

function download_protocol {
  local module="$1"
  curl -OL "https://repo1.maven.org/maven2/com/akkaserverless/akkaserverless-$module-protocol/$framework_version/akkaserverless-$module-protocol-$framework_version.zip"
  unzip "akkaserverless-$module-protocol-$framework_version.zip"
  cp -r "akkaserverless-$module-protocol-$framework_version"/* proto
  rm -rf "akkaserverless-$module-protocol-$framework_version.zip" "akkaserverless-$module-protocol-$framework_version"
}

# Download and unzip the proxy and SDK protocols to the proto directory
download_protocol sdk
download_protocol proxy

# Compile protobuf
#./scripts/compile-protobuf.sh
