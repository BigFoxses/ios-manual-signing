#!/bin/bash
echo "THIS SCRIPT IS USED TO DISPLAY ENTITLEMENT OF APPDOME PRESIGNED IPA"
if [ "$1" == "" ]; then
    echo "Usage ent <xx.ipa>"
    exit -1
fi 
TMP_DIR=$(mktemp -d)
unzip $1 -d $TMP_DIR &> /dev/null
IFS='
'
for i in `find $TMP_DIR -name entitlement\*.plist` ; do
    echo "*********************"
    echo $i
    cat $i
done
rm -rf $TMP_DIR
