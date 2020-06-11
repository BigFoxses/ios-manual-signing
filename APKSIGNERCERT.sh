#!/bin/bash
if [ $# -eq 0 ] ; then
    echo "Please enter the name of APK"
    exit -1
fi
if ! [ -f $1 ]; then
    echo "APK $1 does not exist !! "
    exit -1
fi
TMP_DIR=$(mktemp -d)
unzip $1 -d $TMP_DIR &>  /dev/null
CERT=$(find $TMP_DIR -name \*.RSA -exec keytool -printcert -file  '{}' \;)
#echo $CERT
CERT_SHA1=$(echo $CERT | sed 's/.*SHA1:\(.*\)SHA256:.*/\1/')
#CERT_SHA1=$(echo $CERT | grep SHA1 | cut -f 2)
echo "SIGNING CERT SHA1 = $CERT_SHA1 "
rm -rf $TMP_DIR
