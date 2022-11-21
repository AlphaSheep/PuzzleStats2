# Append characters to force it to appear as a tar file
( printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" ; tail -c +25 backup.ab ) > androidPlusTimer.tar

# Extract the tar
tar -xf androidPlusTimer.tar

# Remove the meta data (makes the next command easier)
rm apps/com.pluscubed.plustimer/f/db_solves.cblite2/db.forest.meta

# Dump the database
./forestdb/build/forestdb_dump --kvs default --hex-body  apps/com.pluscubed.plustimer/f/db_solves.cblite2/db.forest.* > androidPlusTimer.txt

# Clean up
rm ./androidPlusTimer.tar
rm -rf ./apps

# Convert to CSV
./forestDBdumpToJSON.py
