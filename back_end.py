# Code written by Victor Henkow, August 2023
# Version v1.0-beta

# This is the first working version of the code, bugs and other mistakes is therefore expected.
# Already planned future improvements:
#   remove a specific purchase
#   edit a user's info
#   edit a product's price and name
#   change password of an admin
#   work directly with database files instead of converting to dictionary

from files import *
import time
import os


class User:
    def __init__(self, name):
        # users = {"name": {"balance": balance, "email": E-mail, "total": total_spent}}
        self.file_name = self.getFileName()

        self.name = (name.lower()).strip()
        self.users = readToDict(self.file_name)  # Dictionary of all the users from saved file

        self.user_exist = existInDict(self.name, self.users)  # Does the user exist or not

        self.history_file = self.getHistoryFileName()
        if self.user_exist:
            self.history = readToDictList(self.history_file)

    # returns the name of the file with all the users
    @staticmethod
    def getFileName():
        return "saves/users.pkl"

    def getHistoryFileName(self):
        return "saves/history/" + self.name + "_history.pkl"

    def getHistory(self):
        return self.history

    @staticmethod
    def addHistory(dic, file_name, name, action, barcode, product_name, amount):
        time_stamp = time.ctime(time.time())

        # the history of the last 100 events are saved, after that the oldest events gets deleted
        if len(dic["time"]) > 100:  # can check the length of any of the lists since they are all the same length
            del dic["time"][0]
            del dic["name"][0]
            del dic["action"][0]
            del dic["barcode"][0]
            del dic["product name"][0]
            del dic["amount"][0]

        dic["time"].append(time_stamp)
        dic["name"].append(name)
        dic["action"].append(action)
        dic["barcode"].append(barcode)
        dic["product name"].append(product_name)
        dic["amount"].append(amount)

        save(dic, file_name)

    def getName(self):
        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            return self.name

    def getEmail(self):
        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            email = self.users[self.name]["email"]
            return email

    def getBalance(self):
        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            balance = self.users[self.name]["balance"]
            return balance

    def getTotal(self):
        return self.users[self.name]["total"]

    def updateBalance(self, price):
        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            # balance updated successfully
            self.users[self.name]["balance"] -= price
            save(self.users, self.file_name)

    def buy(self, barcode):
        product = Product(barcode)
        price = product.getPrice()

        if not self.user_exist:
            # user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            # successful buy
            self.users[self.name]["total"] += price  # no need to save since updateBalance() saves the same file
            self.updateBalance(price)

            User.addHistory(self.history, self.history_file, self.name, "purchase", barcode,
                            product.getName(), price)

    def removeLastBuy(self):
        if not self.user_exist:
            # the user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            last_name = self.history["name"][-1]
            if not last_name == self.name:
                # last balance edit was not made by the user
                raise ValueError("The last edit of the user's balance was not made by the user.")
            else:
                last_amount = self.history["amount"][-1]

                self.updateBalance(-last_amount)
                User.addHistory(self.history, self.history_file, self.name, "revert last purchase", "",
                                "", -last_amount)

                # remove the last purchase from the total spent
                self.users[self.name]["total"] -= last_amount
                save(self.users, self.file_name)

    # should only be called from Admin
    def addUser(self, email):
        if self.name == "":
            # not an acceptable name error
            raise ValueError("A name cannot be an empty String.")
        elif self.name == "admin":
            # not an acceptable name error, the username admin is used to open the admin menu
            raise ValueError("The name cannot be admin.")
        elif not self.user_exist:
            # new user added successfully
            # A new user always have 0 balance
            self.users[self.name] = {"balance": 0, "email": email.lower(), "total": 0}
            save(self.users, self.file_name)

            # time is the local time when the action happened
            # name is the name of the user or admin that makes the change
            # actions is either purchase or edit by admin
            # barcode and product are the barcode and name of the product, if it is an edit they are empty
            # amount is the amount the balance has been changed with
            # every time a balance change is made it is appended to each of the lists
            history = {"time": [], "name": [], "action": [], "barcode": [], "product name": [], "amount": []}
            save(history, self.history_file)
        else:
            # user already exist
            raise ValueError("A user with the name " + self.name + " already exist.")

    # should only be called from Admin
    # returns the users info
    def removeUser(self):
        if not self.user_exist:
            # the user does not exist error
            raise KeyError("The user " + self.name + " does not exist.")
        else:
            # remove the user
            removed_user = self.users.pop(self.name)
            save(self.users, self.file_name)

            email = removed_user["email"]
            balance = removed_user["balance"]
            total = removed_user["total"]

            # remove the history file
            os.remove(self.history_file)

            return email, balance, total


# A custom error for when the admin is not logged in
class AdminLoginError(Exception):
    pass


class Admin:
    def __init__(self, name, password):
        # admins = {name: {"password": password}}
        self.file_name = "saves/admins.pkl"

        self.name = (name.lower()).strip()
        self.password = password

        self.admins = readToDict(self.file_name)
        self.admin_exist = existInDict(self.name, self.admins)
        self.logged_in = self.login()

    # returns True if the login was successful and False if it failed
    def login(self):
        if not self.admin_exist:
            # We cannot raise an error here because it would break the addAdmin() function
            return False
        else:
            correct_password = self.password == self.admins[self.name]["password"]
            if not correct_password:
                return False
            else:
                return True

    # returns True if the input password equals the password for the admin
    def checkPassword(self, password):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            return password == self.admins[self.name]["password"]

    def changePassword(self, password):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            self.admins[self.name]["password"] = password
            save(self.admins, self.file_name)

    # returns a dictionary of all the admins
    def getAllAdmins(self):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            return self.admins

    # returns a dictionary of all the users
    def getAllUsers(self):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            file_name = User.getFileName()
            return readToDict(file_name)

    # returns a dictionary of all the products
    def getAllProducts(self):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            file_name = Product.getFileName()
            return readToDict(file_name)

    def getName(self):
        if not self.admin_exist:
            # admin does not exist error
            raise KeyError("The admin " + self.name + " does not exist.")
        else:
            return self.name

    def addUser(self, new_name, email):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            new_user = User(new_name)
            new_user.addUser(email)

    # removes the user and returns the users info
    def removeUser(self, name):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            user = User(name)
            email, balance, total = user.removeUser()
            return name, email, balance, total

    def addAdmin(self, new_name, password):
        if self.name == "":
            # not an acceptable name error
            raise ValueError("A name cannot be an empty String.")
        elif not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            admin_exist = existInDict(new_name, self.admins)
            if not admin_exist:
                # admin added
                # The password is stored in plain text which is not optimal, but in this case it is fine I would say.
                self.admins[new_name] = {"password": password}
                save(self.admins, self.file_name)
            else:
                # admin already exist error
                raise ValueError("An admin with the name " + new_name + " already exist.")

    # the method returns the name
    def removeAdmin(self, name):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            admin = self.admins.get(name)

            if admin is not None:
                self.admins.pop(name)
                save(self.admins, self.file_name)
                return name
            else:
                # the admin does not exist error
                raise KeyError("No admin with the name of " + name + " exist.")

    def addBalance(self, name, added_amount):
        if not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            user = User(name)
            # It is a negative amount because updateBalance() normally removes a price
            user.updateBalance(-added_amount)

            history_file = user.getHistoryFileName()
            history = readToDictList(history_file)
            User.addHistory(history, history_file, self.name, "edit by admin", "", "",
                            -added_amount)

    def addProduct(self, new_barcode, new_name, price):
        if not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            new_product = Product(new_barcode)
            new_product.addProduct(new_name, price)

    # returns the info of the product
    def removeProduct(self, barcode):
        if not self.logged_in:
            # admin not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            product = Product(barcode)
            name, price = product.removeProduct()
            return barcode, name, price

    # updates the price and returns the old one
    def updateProductPrice(self, barcode, new_price):
        if not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            product = Product(barcode)
            old_price = product.updatePrice(new_price)
            return old_price

    # updates the name and returns the old one
    def updateProductName(self, barcode, new_name):
        if not self.logged_in:
            # not logged in error
            raise AdminLoginError("Admin " + self.name + " is not logged in.")
        else:
            product = Product(barcode)
            old_name = product.updateName(new_name)
            return old_name


class Product:
    def __init__(self, barcode):
        # products = {barcode: {"name": name, "price": price}}
        self.file_name = self.getFileName()

        self.barcode = (str(barcode).lower()).strip()
        self.products = readToDict(self.file_name)

        self.product_exist = existInDict(self.barcode, self.products)

    # returns the name of the file with all the products
    @staticmethod
    def getFileName():
        return "saves/products.pkl"

    def getBarcode(self):
        if not self.product_exist:
            # product does not exist error
            raise KeyError("There is no product with the barcode " + self.barcode)
        else:
            return self.barcode

    def getName(self):
        if not self.product_exist:
            raise KeyError("There is no product with the barcode " + self.barcode)
        else:
            return self.products[self.barcode]["name"]

    def getPrice(self):
        if not self.product_exist:
            # product does not exist error
            raise KeyError("There is no product with the barcode " + self.barcode)
        else:
            return self.products[self.barcode]["price"]

    # should only be called from Admin, maybe there is a better way to do this
    def addProduct(self, name, price):
        if self.barcode == "000" or self.barcode == "":
            # not an acceptable name error
            raise ValueError("A barcode cannot be an empty String or exit")  # "exit" is used as a cancel command
        elif price < 0:
            # price must be positive
            raise ValueError("The price cannot be negative.")
        elif not self.product_exist:
            # product added successfully
            self.products[self.barcode] = {"name": name, "price": price}
            save(self.products, self.file_name)
        else:
            # product already exist error
            raise ValueError("A product with the barcode " + self.barcode + " already exist.")

    # should only be called from Admin
    # returns the products info
    def removeProduct(self):
        if not self.product_exist:
            raise KeyError("There is no product with the barcode " + self.barcode)
        else:
            removed_product = self.products.pop(self.barcode)
            save(self.products, self.file_name)

            name = removed_product["name"]
            price = removed_product["price"]

            return name, price

    # should only be called from Admin
    # returns the old price
    def updatePrice(self, new_price):
        if not self.product_exist:
            raise KeyError("There is no product with the barcode " + self.barcode)
        else:
            old_price = self.getPrice()
            self.products[self.barcode]["price"] = new_price
            save(self.products, self.file_name)
            return old_price

    # should only be called from Admin
    # returns the old name
    def updateName(self, new_name):
        if not self.product_exist:
            raise KeyError("There is no product with the barcode " + self.barcode)
        else:
            old_name = self.getName()
            self.products[self.barcode]["name"] = new_name
            save(self.products, self.file_name)
            return old_name
