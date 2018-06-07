#!/bin/bash

analyze=staticdep.py
parse=parsejson.py
libtest=libtest
objectlist=objectlist.txt

echo "1. ANALYZE THE STATIC LIBRARY AND PRINT A SUMMARY"
python3 ../$analyze $libtest.a -s
echo

echo "2. LIST OBJECT FILES WITHOUT DEPENDENCIES"
python3 ../$parse $libtest.json
echo

echo "3. LIST EMPTY OBJECT FILES"
python3 ../$parse $libtest.json -e
echo

echo "4. VERIFY THAT A LIST OF OBJECT FILES IS COMPLETE"
python3 ../$parse $libtest.json -v $objectlist
