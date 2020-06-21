#!bin/bash
DIR=$PWD
if ! [ "$1" == ""  ] ; then
    DIR="$1"
fi
IFS='
'
for i in `find $DIR  -exec file '{}' \; | grep -i mach | cut -d":" -f 1 | cut -d"(" -f 1 | awk '{$1=$1;print}'|  sort -u -k1`; do
    echo "************************"
    echo $i
    codesign -d --ent :- $i
done
