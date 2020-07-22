for dt in `seq 0.1 0.1 10`; do
	echo "'dana_forcing_+${dt}K.nc'" > forcing_file_list_+${dt}K.txt
done
