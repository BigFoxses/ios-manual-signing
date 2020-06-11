#!/bin/bash
mkdir tmp
cp $1 tmp
(cd tmp; mkdir -p tmp-ipa; ar vx $1; tar zxf data.tar.lzma -C tmp-ipa )
(cd tmp/tmp-ipa; mv Applications Payload)
(cd tmp/tmp-ipa; zip -r ../../$1.ipa .)
rm -rf tmp
