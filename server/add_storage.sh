#!/bin/bash

NAME=$1
if [ "x$NAME" == "x" ] ; then
	echo "Usage: $0 destination_name"
	exit 1
fi
mkdir -p ./store/$NAME
echo "Added storage: $NAME"
