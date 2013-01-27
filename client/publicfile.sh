#!/bin/bash

DIGEST=$1
FNAME=$2
PASSWORD=$3
HOST="localhost:5000"
if [ "x$4" != "x" ] ; then
	HOST=$4
fi

function usage
{
	echo -e "Usage:\n    $0 digest file_to_public password [host]\n"
	exit 1
}

if [ "x$PASSWORD" == "x" ] ; then
	usage
fi
if [ "x$FNAME" == "x" ] ; then
	usage
fi

CHALL="$RANDOM$RANDOM$RANDOM"
RESP=$(echo -n $PASSWORD$CHALL|sha256sum|cut -d' ' -f1)

if [[ "$HOST" != *"http"* ]] ; then
	HOST="https://$HOST"
fi
url=$(curl -s -X POST -k -F challenge="$CHALL" $HOST/public/$DIGEST/$RESP/$FNAME)
echo $url
