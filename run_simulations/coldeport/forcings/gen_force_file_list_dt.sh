zero=0
for dt in `seq -4 1 4`; do
  if (( "$dt" < "$zero")); then
	echo "'col-de-port_1993-2011_${dt}.0K.nc'" > forcing_file_list_${dt}.0K.txt
  else
	echo "'col-de-port_1993-2011_+${dt}.0K.nc'" > forcing_file_list_+${dt}.0K.txt
  fi
done
