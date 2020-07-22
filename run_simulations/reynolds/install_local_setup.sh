#!/usr/bin/env bash
#
# This script will localize the file manager
# so that all of the paths are localized to
# the current location of the template repo.
zero=0
for dt in `seq -4 2 4`; do
  if (( "$dt" < "$zero")); then
    sed "s/==/${dt}.0/g" template_file_manager.txt > file_manager_${dt}.0K.txt
    sed -i "s|PWD|$(pwd)|g" file_manager_${dt}.0K.txt
  else
    sed "s/==/+${dt}.0/g" template_file_manager.txt > file_manager_+${dt}.0K.txt
    sed -i "s|PWD|$(pwd)|g" file_manager_+${dt}.0K.txt
  fi
done
