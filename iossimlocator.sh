#!/bin/bash
## possible arguments - entilement-file , mobile-provisioning fille optional -
# if not supplied
# assume entitlement file could be extracted from binary file . would abort if this is not the case.
# assume  mobileprovsioning file exist , if not abort
BOOTED_UDID=$(xcrun simctl list |  grep -i boot | head -n 1|  sed "s/(/|/g" | sed "s@)@|@g" | cut -d'|' -f4)
if [ "$BOOTED_UDID" == "" ]; then
    echo "NO BOOTED DEVICE FOUND"
    exit
fi
echo "** BOOTED DEVICE -- UDID is $BOOTED_UDID"
SIMUALTOR_PATH_PREFIX="$HOME/Library/Developer/CoreSimulator/Devices"
SIMULATOR_PATH="$SIMUALTOR_PATH_PREFIX/$BOOTED_UDID/data"
echo "** SIMULATOR_PATH --  $SIMULATOR_PATH"
read -p "Press enter to continue"
echo "$SIMULATOR_PATH" | pbcopy
ls -Ral $SIMULATOR_PATH
