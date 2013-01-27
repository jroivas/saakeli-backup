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
	echo -e "Usage:\n    $0 digest file_to_update keyfile password [host]\n"
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

if [ -f "$CRYPTED" ] ; then
	openssl aes-256-cbc -in "$FNAME" -out "$CRYPTED" -kfile "$KEYFILE"
	basefile=$(basename "$FNAME")
	outfile=$(curl -s -X POST -k -F filedata=@"$CRYPTED" -F challenge="$CHALL" $HOST/update/$DIGEST/$RESP/$basefile)
	rm -f "$CRYPTED"
	echo $outfile
fi
