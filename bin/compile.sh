./bin/prepare.sh

for file in *_pb2*; do rm "$file"; done

for file in *.proto; do python -m grpc_tools.protoc --proto_path=./proto  --proto_path=. --python_out=. --grpc_python_out=.  $file; done

for file in *_pb2*; do perl -i -pe 's/from akkaserverless/from akkaserverless.akkaserverless/g' $file; done
