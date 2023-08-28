# Code written by Victor Henkow, August 2023

# To create all the files necessary, this script needs to be run before the first start of gui_main

from files import *
import os


def create_directories():
    os.mkdir("./saves")
    print("Save directory created.\n")

    os.mkdir("./backups")
    print("Backup directory created.\n")


# manually creates the user dictionary and history directory
def create_user():
    # something needs to be saved and admin is an illegal name, so lets use that
    users = {"admin": {"balance": None, "email": None, "total": None}}
    save(users, "saves/users.pkl")

    os.mkdir("./saves/history")
    print("Users file created and saved, and history directory created.\n")


# manually creates the products dictionary
def create_product():
    # something needs to be saved and 000 is an illegal barcode, so lets use that
    products = {"000": {"name": None, "price": None}}
    save(products, "saves/products.pkl")

    print("Products file created and saved.\n")


# manually creates the admin dictionary
def create_admin():
    print("Please fill in the following information about the first admin.")
    name = input("Name: ")
    password = input("Password: ")
    admins = {name: {"password": password}}
    save(admins, "saves/admins.pkl")

    print("Admins file created and saved.\n")


# manually creates the settings file
def create_settings():
    print("Please fill in the following information about the starting settings.")
    title = input("Title of the GUI window: ")
    first_timeout = input("First timeout [ms]: ")
    second_timeout = input("Second timeout [ms]: ")
    # need to put the dictionary in a list to make the save function work
    settings = [{"title": title, "first timeout": first_timeout, "second timeout": second_timeout}]
    save(settings, "settings.pkl")

    print("Settings file created adn saved.\n")


if __name__ == "__main__":
    save_exist = os.path.isdir("saves")
    backups_exist = os.path.isdir("backups")

    if save_exist:
        print("The directory saves or backups seems to already exist. To prevent the program from overwriting existing"
              + "\nfiles it has stopped itself from running. If you which for to run this file, please make sure that"
              + "\nthe directories saves and backups are removed.")
    else:
        create_directories()
        create_user()
        create_product()
        create_admin()
        create_settings()

        print("You can now run gui_main.py. You can add users, admins and products by logging in as an admin. To log\n"
              + "in as an admin, type 'admin' in the username window and the admin log in menu will open. The program\n"
              + "logs everything printed in the terminal in the file 'log.txt'.")
