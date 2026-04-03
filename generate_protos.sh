#!/bin/bash

# Define paths relative to the project root
PROTO_DIR="./proto"
PY_OUT="./service-1-python"
GO_OUT="./service-2-go"

echo "Creating output directories if they don't exist..."
mkdir -p $PY_OUT/gen/iot_pb
mkdir -p $GO_OUT/gen/iot_pb

echo "Compiling Protobuf for Python..."
# Python just needs the output directory specified
protoc --proto_path=$PROTO_DIR \
       --python_out=$PY_OUT/gen/iot_pb \
       $PROTO_DIR/sensor.proto

echo "Compiling Protobuf for Go..."
# Go requires the paths=source_relative flag to align with your go.mod
protoc --proto_path=$PROTO_DIR \
       --go_out=$GO_OUT/gen/iot_pb \
       --go_opt=paths=source_relative \
       $PROTO_DIR/sensor.proto

echo "✅ Compilation complete! Check the /gen directories in both services."