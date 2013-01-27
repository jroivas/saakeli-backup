#!/bin/bash

DIGEST=$1
FNAME=$2
PASSWORD=$3
HOST="localhost:5000"
if [ "x$4" != "x" ] ; then
	HOST=$4
fi

dir=$(dirname $0)
source ${dir}/tools.sh

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

#if [[ "$HOST" != *"http"* ]] ; then
#	HOST="https://$HOST"
#fi
checkhost

challenge
#CHALL="$RANDOM$RANDOM$RANDOM"
#RESP=$(echo -n $PASSWORD$CHALL|sha256sum|cut -d' ' -f1)
verify=$(curl -s -X POST -k -F challenge="$CHALL" $HOST/remove/$DIGEST/$RESP/$FNAME|cut -d' ' -f2)

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

#CHALL="$RANDOM$RANDOM$RANDOM"
#RESP=$(echo -n $PASSWORD$CHALL|sha256sum|cut -d' ' -f1)
challenge
res=$(curl -s -X POST -k -F challenge="$CHALL" -F confirm="$verify" $HOST/remove/$DIGEST/$RESP/$FNAME)
echo $res
