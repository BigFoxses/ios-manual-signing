#!/bin/bash
## possible arguments - entilement-file , mobile-provisioning fille optional -
# if not supplied
# assume entitlement file could be extracted from binary file . would abort if this is not the case.
# assume  mobileprovsioning file exist , if not abort
DEF_MOBILE_PROVISION_FILE="embedded.mobileprovision"
MOBILE_PROVISION_FILE=
TMP_DIR=".tmp" 
mkdir -p $TMP_DIR
IPA_FILE=
ENTILEMENT_FILE=
ARG=0
usage() {

    echo "Resign.sh -p|--provision <mobile-provision-file> -e|--ent <entitlement file>  -i |--ipa <ipa file to be resigned"
    exit 1
}
while [ "$1" != "" ]; do
  case $1 in 
    -p | --provision )      shift 
                            MOBILE_PROVISION_FILE=$1 
                            ARG=$((ARG+1))
                            ;;
    -e | --ent )            shift
                            ENTILEMENT_FILE=$1
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
CURRENT_DIR=$PWD
echo "$CURRENT_DIR"
if [  "$ENTILEMENT_FILE" == "" ] || ! [ -f $ENTILEMENT_FILE ]; then 
    echo "ENTITLEMENT FILE has not been specified or does not exist. "
    usage
fi     
if [ "$MOBILE_PROVISION_FILE" == "" ] || ! [ -f $MOBILE_PROVISION_FILE ] ; then
    echo "MOBILE PROVISION file does not exist" 
    usage
fi 
unzip -o -q $IPA_FILE -d $TMP_DIR
cp $MOBILE_PROVISION_FILE ${TMP_DIR}/Payload/${IPA_EXECUTABLE}.app/$DEF_MOBILE_PROVISION_FILE

## get the code signer -development or distribution
#Payload/OfflineOTP-axn.app/Frameworks/DYMobileCore.framework

CODE_SIGNER_HASH=$(security find-identity -p codesigning -v  | grep -i  "Apple Development" | awk '{print $2}')
FRAMEWORK_LOC="Payload/${IPA_EXECUTABLE}.app/Frameworks"
for i in $(find ${TMP_DIR} -type d  -name "*.framework") ; do
    codesign -f -v -s $CODE_SIGNER_HASH $i
done
codesign -f -v --entitlements $PWD/entilements.xml -s $CODE_SIGNER_HASH ${TMP_DIR}/Payload/${IPA_EXECUTABLE}.app
# zip package
(cd $TMP_DIR; zip -qr ../${IPA_EXECUTABLE}.ipa.resign .) 
echo "Resign completed. The resigned package is ${IPA_EXECUTABLE}.ipa.resign "
rm -rf $TMP_DIR
