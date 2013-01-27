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
	echo -e "Usage:\n    $0 digest matchrules password [host]\n"
	exit 1
}

if [ "x$PASSWORD" == "x" ] ; then
	usage
fi
if [ "x$FNAME" == "x" ] ; then
	usage
fi

checkhost
challenge

#curl -s -X POST -k -F challenge="$CHALL" $HOST/list/$DIGEST/$RESP/$FNAME
curl -X POST -k -F challenge="$CHALL" $HOST/list/$DIGEST/$RESP/$FNAME
