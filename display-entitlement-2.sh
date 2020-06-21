#!/bin/bash
echo "THIS SCRIPT IS USED TO DISPLAY ENTITLEMENT OF An IPA"
if [ "$1" == "" ]; then
    echo "Usage ent2 <xx.ipa>"
    exit -1
fi 
TMP_DIR=$(mktemp -d)
unzip $1 -d $TMP_DIR &> /dev/null
IFS='
'
for i in `find $TMP_DIR  -exec file '{}' \; | grep -i mach | cut -d":" -f 1 | cut -d"(" -f 1 | awk '{$1=$1;print}'|  sort -u -k1`; do
    echo "************************"
    echo $i
    codesign -d --ent :- $i
done
