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
	echo -e "Usage:\n    $0 digest file_to_remove keyfile password [host]\n"
	exit 1
}

if [ "x$PASSWORD" == "x" ] ; then
	usage
fi
if [ "x$FNAME" == "x" ] ; then
	usage
fi
if [ ! -e "$KEYFILE" ] ; then
	usage
fi


CHALL="$RANDOM$RANDOM$RANDOM"
RESP=$(echo -n $PASSWORD$CHALL|sha256sum|cut -d' ' -f1)
verify=$(curl -s -X POST -k -F challenge="$CHALL" https://$HOST/remove/$DIGEST/$RESP/$FNAME|cut -d' ' -f2)

if [ "x$verify" == "x" ] || [ "x$verify" == "xFAIL" ] || [ "x$verify" == "xERROR" ] ; then
	echo "Didn't get proper verify code, aborting."
	exit 0
fi

echo "Really remove file: $FNAME, verify code: $verify? (Y/n)"
read resp
if [ "x$resp" != "xy" ] && [ "x$resp" != "xY" ] ; then
	echo "Aborting remove"
	exit 0
fi

CHALL="$RANDOM$RANDOM$RANDOM"
RESP=$(echo -n $PASSWORD$CHALL|sha256sum|cut -d' ' -f1)
res=$(curl -s -X POST -k -F challenge="$CHALL" -F confirm="$verify" https://$HOST/remove/$DIGEST/$RESP/$FNAME)
echo $res
