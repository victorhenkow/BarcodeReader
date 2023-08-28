# BarcodeReader
A program for managing products using a barcode reader. The program should only be used for personal use, like
keeping track of expenses at a dinner party.

To start the program you run gui_main.py. Before the first time you run the program you need to run first_start.py
which creates all the directories and files needed for the program to work. For the program to run correctly, the
barcode reader is supposed to input the numbers and then press the <Return> key.

The script backup.sh creates a backup of the saves folder. To make it run automatically, move the BarcodeReader
directory to the home folder i.e. ~/BarcodeReader. Then set up the backup.sh script to run automatically using 
crontab. This is done by opening crontab using crontab -e, then pasting 01 05 * * * ~/BarcodeReader/backup.sh into 
the file. This makes it run every day at 05:01. The files are saved using the date without the year, so backups will
be saved for one year, then get overwritten.

The program works by taking a username, if the username is 'admin' you get redirected to the admin login screen. When
you have logged in you will see the admin menu, where you can add users, products and admins. To log out, simply click
back until you get back to the first screen. When you have added a user and a product you can make a purchase. This is
done by inserting the username which redirects you to the buy screen. There you can insert the product barcode to make
a purchase. The purchase gets cancelled by either inserting a barcode of '000' or waiting until the first timeout 
runs out. If you make a purchase you can make another one without inserting your username again until the second 
timeout runs out. Recomended values for the first timeout is 12000 ms and for the second timeout is 4000 ms.


