#!/bin/bash

function challenge {
	CHALL="$RANDOM$RANDOM$RANDOM$RANDOM$RANDOM"
	RESP=$(echo -n $PASSWORD$CHALL|sha256sum|cut -d' ' -f1)
}

function checkhost {
	if [[ "$HOST" != *"http"* ]] ; then
		HOST="https://$HOST"
	fi
}

function gettmp {
	CRYPTED=$(tempfile)
}

function tests {
	RESP=""
	HOST="joo"
	challenge
	echo $RESP

	echo $HOST
	checkhost
	echo $HOST

	HOST="http://ur.li"
	checkhost
	echo $HOST

	HOST="https://ur.li"
	checkhost
	echo $HOST
}

#tests
