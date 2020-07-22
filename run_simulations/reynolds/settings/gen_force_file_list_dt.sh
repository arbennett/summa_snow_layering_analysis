zero=0
for dt in `seq -4 1 4`; do
  if (( "$dt" < "$zero")); then
	echo "'forcing_above_aspen_${dt}.0K.nc'" > forcing_file_list_${dt}.0K.txt
  else
	echo "'forcing_above_aspen_+${dt}.0K.nc'" > forcing_file_list_+${dt}.0K.txt
  fi
done
