zero=0
for dt in `seq -4 1 4`; do
  if (( "$dt" < "$zero")); then
    sed "s/==/${dt}.0/g" file_manager_template.txt > file_manager_${dt}.0K.txt
  else
    sed "s/==/+${dt}.0/g" file_manager_template.txt > file_manager_+${dt}.0K.txt
  fi
done
