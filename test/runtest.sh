#!/bin/bash

analyze=staticdep.py
parse=parsejson.py
libtest=libtest
objectlist=objectlist.txt

echo "ANALYZING THE STATIC LIBRARY"
python3 ../$analyze $libtest.a
echo

echo "LISTING OBJECT FILES WITHOUT DEPENDENCIES"
python3 ../$parse $libtest.json
echo

echo "VERYFYING THAT A LIST OF OBJECT FILES IS COMPLETE"
python3 ../$parse $libtest.json -v $objectlist
echo
