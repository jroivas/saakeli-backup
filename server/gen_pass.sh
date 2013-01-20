#!/bin/bash

NAME=$1
if [ "x$NAME" == "x" ] ; then
	echo "Usage: $0 destination_name"
	exit 1
fi
pass=$(echo -n "$RANDOM$RANDOM$RANDOM$RANDOM$RANDOM" | sha256sum | cut -d' ' -f1)
mkdir -p ./store/$NAME
echo $pass > ./store/$NAME/.pass
echo "Password for storage $NAME: $pass"
