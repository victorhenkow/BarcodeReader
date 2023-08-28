#!/bin/sh

# What to backup.
backup_files="saves"

# Create backup archive filename, saves as the day number-month, so it writes over the files after one year
day_month=$(date +%d-%b)
archive_file="$day_month-$backup_files.tar.gz"

# Backup the files using tar. Put in the correct directory here
tar zcvf ~/BarcodeReader/backups/$archive_file ~/BarcodeReader/$backup_files
