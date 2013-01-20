#!/bin/bash

DIGEST=$1
FNAME=$2
KEYFILE=$3
HOST="localhost:5000"
if [ "x$4" != "x" ] ; then
	HOST=$4
fi

function usage
{
	echo -e "Usage:\n    $0 digest file_to_send keyfile [host]\n"
	exit 1
}

if [ ! -e "$FNAME" ] ; then
	usage
fi
if [ ! -e "$KEYFILE" ] ; then
	usage
fi

CRYPTED=$(tempfile)

if [ -f "$CRYPTED" ] ; then
	openssl aes-256-cbc -in "$FNAME" -out "$CRYPTED" -k "$KEYFILE"
	CRYPTED=$FNAME
	outfile=$(curl -s -X POST -k -F filedata=@"$CRYPTED" -F filename=$(basename "$FNAME") -F digest=$DIGEST https://$HOST/store)
	rm -f "$CRYPTED"
	echo $outfile
fi
