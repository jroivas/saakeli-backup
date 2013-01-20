#!/bin/bash

DIGEST=$1
FNAME=$2
KEYFILE=$3
PASSWORD=$4
HOST="localhost:5000"
if [ "x$5" != "x" ] ; then
	HOST=$5
fi

function usage
{
	echo -e "Usage:\n    $0 digest file_to_send keyfile password [host]\n"
	exit 1
}

if [ "x$PASSWORD" == "x" ] ; then
	usage
fi
if [ ! -e "$FNAME" ] ; then
	usage
fi
if [ ! -e "$KEYFILE" ] ; then
	usage
fi

CHALL="$RANDOM$RANDOM$RANDOM$RANDOM"
RESP=$(echo -n $PASSWORD$CHALL|sha256sum|cut -d' ' -f1)
CRYPTED=$(tempfile)

if [ -f "$CRYPTED" ] ; then
	openssl aes-256-cbc -in "$FNAME" -out "$CRYPTED" -kfile "$KEYFILE"
	#outfile=$(curl -s -X POST -k -F filedata=@"$CRYPTED" -F filename=$(basename "$FNAME") -F digest=$DIGEST https://$HOST/store)
	outfile=$(curl -s -X POST -k -F filedata=@"$CRYPTED" -F filename=$(basename "$FNAME") -F challenge="$CHALL" https://$HOST/store/$DIGEST/$RESP)
	rm -f "$CRYPTED"
	echo $outfile
fi
