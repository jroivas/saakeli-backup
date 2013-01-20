#!/bin/bash

# Generate dummy cert
openssl genrsa 2048 > host.key
openssl req -new -x509 -nodes -sha1 -days 3650 -key host.key > host.cert
cat host.cert host.key > host.pem
