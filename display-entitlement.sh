#!/bin/bash
DIR=$PWD
if ! [ "$1" == "" ] ; then
    DIR="$1"
fi
IFS='
'
for i in `find $DIR -name entitlement\*.plist` ; do
    echo "*********************"
    echo $i
    cat $i
done
