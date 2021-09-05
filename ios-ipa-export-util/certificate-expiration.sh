#!/bin/sh
if [ -z $1 ]; then
   echo "Please enter common name of the certificate"
   exit -1
fi
NAME=$1
echo `/usr/bin/security find-certificate -a -c "${NAME}" -p -Z "/Library/Keychains/System.keychain" | /usr/bin/openssl x509 -text | grep -i subject`
certexpdate=$(/usr/bin/security find-certificate -a -c "${NAME}" -p -Z "/Library/Keychains/System.keychain" | /usr/bin/openssl x509 -noout -enddate| cut -f2 -d=)

dateformat=$(/bin/date -j -f "%b %d %T %Y %Z" "$certexpdate" "+%Y-%m-%d %H:%M:%S")

echo "<result>$dateformat</result>"
