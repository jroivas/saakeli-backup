#!/bin/bash

./gen_cert.sh

# Make directory structure
mkdir -p store
./add_storage.sh initial
./gen_pass.sh initial 
