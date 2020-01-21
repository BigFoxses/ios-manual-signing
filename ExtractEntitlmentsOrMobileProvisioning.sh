#!/bin/bash
## possible arguments - entilement-file , mobile-provisioning fille optional -
# if not supplied
# assume entitlement file could be extracted from binary file . would abort if this is not the case.
# assume  mobileprovsioning file exist , if not abort
DEF_MOBILE_PROVISION_FILE="embedded.mobileprovision"
MOBILE_PROVISION_FILE=
ENTILEMENT_FILE=
TMP_DIR=".tmp" 
mkdir -p $TMP_DIR
IPA_FILE=
ARG=0
usage() {

    echo "Resign.sh -p|--provision -e|--ent  -i |--ipa <ipa file to be extracted from "
    exit 1
}
while [ "$1" != "" ]; do
  case $1 in 
    -p | --provision )      
                            MOBILE_PROVISION_FILE="YES"
                            ARG=$((ARG+1))
                            ;;
    -e | --ent )            
                            ENTILEMENT_FILE="YES"
                            ARG=$((ARG+1))
                            ;;
    -i | --ipa)              shift 
                            IPA_FILE=$1
                            ARG=$((ARG=1))
                            ;;
    *)                      usage
                            exit 1
    esac
    shift
done

if  [ "$IPA_FILE" == "" ] || ! [ -f $IPA_FILE ] ; then 
    echo "$IPA_FILE does not exit"
    usage
fi

IPA_EXECUTABLE=$(echo $IPA_FILE | cut -d "." -f 1) 
echo $IPA_EXECUTABLE
unzip -q -o $IPA_FILE -d $TMP_DIR
CURRENT_DIR=$PWD
echo "$CURRENT_DIR"
if [  "$ENTILEMENT_FILE" != "" ]; then 
    find $TMP_DIR -name ${IPA_EXECUTABLE} -exec jtool --ent '{}' \; > $PWD/entilements.xml 
fi 
if [ "$MOBILE_PROVISION_FILE" != "" ]  ; then 
    cp ${TMP_DIR}/Payload/${IPA_EXECUTABLE}.app/$DEF_MOBILE_PROVISION_FILE $PWD
fi 
rm -rf $TMP_DIR
