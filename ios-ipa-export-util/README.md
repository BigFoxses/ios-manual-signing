#!/bin/bash

set -eo pipefail
IFS=$'\n\t'

function Usage()
{
  echo "  ios-ipa-export-from-xarchive <ProjectName> <CodeSigner> <optionlist>  eg.  ios-ipa-export-from-xarchive XARCHIVEFILE iPhone Distribution:xxxxx OPTIONPLISTFILE-JSON "
}

if [ -z $1 ] || [ -z $2 ] || [ -z $3 ]  ;then
     Usage
     exit -1
fi
MyApp=$1
# Constants
NOW=$(date +"%Y%m%d-%H%M")
BUILD_FILE_NAME=$1
SCHEME="${MyApp}"
WORKSPACE="${MyApp}"
PROJECT="${MyApp}"
CONFIGURATION="AdHoc"
PROFILE_NAME="${MyApp}-AdHoc"
CODE_SIGN_IDENTITY_NAME=$2
OPTIONLIST=$3

# Build (project)
#xcodebuild -archivePath "$PWD/${BUILD_FILE_NAME}.xcarchive" -project "${PROJECT}.xcodeproj" -scheme "${SCHEME}" -configuration "${CONFIGURATION}" archive clean

# Build (workspace)
#xcodebuild -archivePath "${BUILD_FILE_NAME}.xcarchive" -workspace "${WORKSPACE}.xcworkspace" -scheme "${SCHEME}" -configuration "${CONFIGURATION}" archive clean

# Export archive (code sign using export options plist to specify bitcode etc)
# Newer but not working in Xcode 8 if you use rvm to set non system Ruby (Error Domain=IDEDistributionErrorDomain Code=14 "No applicable devices found.")
#xcodebuild -exportArchive -exportOptionsPlist "exportOptions-adhoc.plist" -archivePath "${BUILD_FILE_NAME}.xcarchive" -exportPath "${BUILD_FILE_NAME}.ipa"

# Export archive (code sign using profile and code sign identity)
# Legacy but still working (Warning: xcodebuild: WARNING: -exportArchive without -exportOptionsPlist is deprecated)
#xcodebuild -exportArchive -archivePath "${BUILD_FILE_NAME}.xcarchive" -exportPath "${BUILD_FILE_NAME}.ipa" -exportFormat ipa -exportProvisioningProfile "${PROFILE_NAME}"
if [ -z $OPTIONLIST ] ; then
    echo "$OPTIONLIST must not be empty"
    echo "examples: ..."
    exit 1
else
  cat $OPTIONLIST | plutil convert xml1 -o $PWD:ExportOptionList.plist -
  if [ $? -eq 0 ]; then
	xcodebuild -exportArchive -archivePath "${BUILD_FILE_NAME}.xcarchive" -exportPath "${BUILD_FILE_NAME}.ipa"  -exportOptionsPlist $PWD:ExportOptionList.plist
  else
    echo "fail to generate ExportOptionList.plist"
fi
