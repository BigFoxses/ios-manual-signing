#!/bin/bash
if [ $# -lt 2 ]; then 
    echo "usage extractProfile <xxx.ipa> <OUTPUT_PROV_DIR>"
    exit -1
fi
FILE=$1
OUTPUT_DIR=$2 
[[ -d "$OUTPUT_DIR" ]] && rm -rf $OUTPUT_DIR ||  mkdir -p "$OUTPUT_DIR" 
mkdir -p $OUTPUT_DIR
#echo $OUTPUT_DIR
TMP_DIR=$(mktemp -d)
unzip $FILE -d $TMP_DIR &> /dev/null
IFS='
'
for i in `find $TMP_DIR -name \*.mobile\* `; do
 #   echo $i
    DIR_NAME=$(dirname $i)
    SUFFIX_NAME=$(basename $i)
    PREFIX_NAME=$(basename $DIR_NAME)
    FILE_NAME="$PREFIX_NAME.""$SUFFIX_NAME"
    FINAL=$(echo $FILE_NAME | tr ' ' '-')
    mv -- $i $OUTPUT_DIR/$FINAL
    security cms -D -i $OUTPUT_DIR/$FINAL
#    echo $FINAL
done
[[ -d $TMP_DIR ]] && rm -rf $TMP_DIR
[[ -d $OUTPUT_DIR ]] && ls -al $OUTPUT_DIR