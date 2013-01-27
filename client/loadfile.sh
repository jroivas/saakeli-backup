#!/bin/bash

DIGEST=$1
FNAME=$2
KEYFILE=$3
PASSWORD=$4
HOST="localhost:5000"
if [ "x$5" != "x" ] ; then
	HOST=$5
fi
dir=$(dirname $0)
source ${dir}/tools.sh

function usage
{
	echo -e "Usage:\n    $0 digest file_to_fetch keyfile password [host]\n"
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

checkhost
challenge
gettmp

curl -X POST -s -k -F challenge=$CHALL $HOST/load/$DIGEST/$RESP/$FNAME > $CRYPTED
tmp=$(grep "Not found" $CRYPTED)

if [[ "$tmp" != *"Not found"* ]] && [ ! -z "$CRYPTED" ] ; then
	cat $CRYPTED | openssl aes-256-cbc -d -kfile "$KEYFILE"
else
	echo "FAILED $tmp"
fi
rm -f $CRYPTED
