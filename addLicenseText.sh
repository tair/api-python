#!/bin/bash

#TO-DO
#Remove all <License> tags. Find any shebang statements. 
#Add license text (license.txt) with <License> tag after shebang statements

find . -name \*.py | perl -ne 'chomp; `cp $_ .tmp; cat license.txt .tmp > $_;`'
