#!/bin/bash
FILE=$1
IPA=$2
if [ ! -f "$1" ] ; then
    echo "Appdome sign scripts does not exist"
    exit -1
fi
[[ -f $IPA ]] && rm -f $IPA
function extract_payload() {
     match=`grep --text --line-number "^PAYLOAD:$" "${1}" | cut -d ":" -f 1`
     payload_start=$((match + 1))
     tail -n +${payload_start} "${1}"
 }
[[ -f $IPA ]] && rm -f $IPA
extract_payload $FILE > $IPA
