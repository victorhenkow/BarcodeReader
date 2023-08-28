# Code written by Victor Henkow, August 2023
# Version v1.0-beta

# This version of the code is meant for testing, it does not include every feature of the back_end module. It can add
# users, admins and product; remove users, admins and products; add balance to a user.
# Already planned future improvements:
#   improve the GUI look
#   general improvement to the structure of the code
#   add a flash of green screen if purchase was successful, otherwise a flash of a red screen
#   admin can see users full history
#   admin can see all users
#   admin can see all admins
#   admin can see all products
#   bind "<Return>" to every submit button
#   right now the settings.pkl file was manually created, an admin should be able to change the settings
#   a different message should be printed depending on if a user times out due to the first or second timeout

# Code info:
# **********************************************************************************************************************
# Everything that is printed to the terminal is logged in the file log.txt
# Each class is a frame, and every frame is a different page in the menu.
# Function with event=None have it because it is needed to make binding "<Return>" to the function work

import tkinter as tk
from back_end import *
from files import *


class Windows(tk.Tk):
    def __init__(self, first_page, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # importing the settings file to a dictionary
        # every setting is a list, so it needs to be called by settings["whatever option"][0]
        settings = self.getSettings()

        # Adding a title to the window
        self.wm_title(settings["title"][0])

        # creating a frame and assigning it to container
        self.container = tk.Frame(self, height=400, width=600)
        # specifying the region where the frame is packed in root
        self.container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_page(first_page)

    def show_page(self, page, *args):
        frame = page(self.container, self, *args)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    @staticmethod
    def getSettings():
        return readToDictList("settings.pkl")


class ScanUserPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.login)

        self.name = tk.StringVar()  # the name which the user inputs

        self.createGraphics()

    def createGraphics(self):
        name_label = tk.Label(self, text="Username")
        name_entry = tk.Entry(self, textvariable=self.name)

        submit_button = tk.Button(self, text="Submit", command=self.login)

        name_entry.focus_set()

        name_label.pack()
        name_entry.pack()
        submit_button.pack()

    def login(self, event=None):
        name = self.name.get()

        if name == "admin":
            print("Admin login menu opened.")
            self.controller.show_page(AdminLoginPage)
        else:
            try:
                # check if the user exist
                user = User(name)
                name = user.getName()
            except KeyError as error:
                print("An error occurred: " + str(error))
                self.controller.show_page(ScanUserPage)
            else:
                print("User " + name + " has started a purchase.")
                settings = Windows.getSettings()
                self.controller.show_page(ScanProductPage, user, int(settings["first timeout"][0]))


class ScanProductPage(tk.Frame):
    def __init__(self, parent, controller, user, timeout):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.buy)

        self.settings = Windows.getSettings()

        self.user = user  # the user who is going to buy
        self.username = self.user.getName()
        self.balance = self.user.getBalance()
        self.total = self.user.getTotal()
        self.history = self.user.getHistory()

        self.barcode = tk.StringVar()  # the name which the user inputs

        # a timeout for buying
        self.timeout = self.after(timeout, lambda reason=", timed out": self.back(reason))
        self.timer = self.after(0, self.countdown)
        self.count = int(timeout / 1000 + 1)  # needs to have +1 since countdown always takes -1 from self.count
        self.count_var = tk.IntVar()

        self.createGraphics()

    def createGraphics(self):
        barcode_label = tk.Label(self, text="Welcome " + self.username + "! Scan a product barcode. \n Balance: " +
                                            str(self.balance) + " kr")
        barcode_entry = tk.Entry(self, textvariable=self.barcode)
        countdown_label = tk.Label(self, textvariable=self.count_var)
        submit_button = tk.Button(self, text="Submit", command=self.buy)

        barcode_entry.focus_set()

        barcode_label.pack()
        barcode_entry.pack()
        countdown_label.pack()
        submit_button.pack()

        # display the last 4 purchases
        history_title_label = tk.Label(self, text="\n History \n----------------------")
        history_title_label.pack()
        try:  # The user may not have four items in its history
            for i in range(1, 5):
                time_stamp = self.history["time"][-i]
                barcode = self.history["barcode"][-i]
                name = self.history["product name"][-i]
                price = str(self.history["amount"][-i])
                history_label = tk.Label(self, text=time_stamp + "\n" + barcode + ", " + name + ", " + price +
                                                    " kr \n\n")

                history_label.pack()
        except IndexError:
            pass  # No problem if the user does not have enough purchase history, just don't display it

    def countdown(self):
        self.count -= 1
        self.count_var.set(self.count)

        # counts down every second
        self.timer = self.after(1000, self.countdown)

    def back(self, reason=""):
        self.after_cancel(self.timer)

        print("Purchase cancelled" + reason)
        self.controller.show_page(ScanUserPage)

    def buy(self, event=None):
        barcode = self.barcode.get()

        if barcode == "000":
            self.back(" by user.")
        else:
            try:
                product = Product(barcode)
                name = product.getName()
                price = product.getPrice()
            except KeyError as error:
                print("An error occurred: " + str(error))
                self.after_cancel(self.timeout)
                self.after_cancel(self.timer)
                self.controller.show_page(ScanProductPage, self.user, int(self.settings["second timeout"][0]))
            else:
                self.user.buy(barcode)

                balance = str(self.user.getBalance())
                total = str(self.user.getTotal())

                print("Purchase successful!\tItem barcode: " + barcode + " | Item name: " + name + " | Item price: "
                      + str(price) + " kr | User balance: " + str(balance) + " kr | User total spent: " + str(total) +
                      " kr")

                # after you have bought something you have time to buy more things without scanning the username again
                # first the old timeout needs to be cancelled, then we set a new lower time one for each new purchase
                self.after_cancel(self.timeout)
                self.after_cancel(self.timer)
                self.controller.show_page(ScanProductPage, self.user, int(self.settings["second timeout"][0]))


class AdminLoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.login)

        self.name = tk.StringVar()  # the name which the admin inputs
        self.password = tk.StringVar()  # the password which the admin inputs

        self.createGraphics()

    def createGraphics(self):
        name_label = tk.Label(self, text="Username")
        name_entry = tk.Entry(self, textvariable=self.name)

        password_label = tk.Label(self, text="Password")
        password_entry = tk.Entry(self, textvariable=self.password, show="*")

        submit_button = tk.Button(self, text="Submit", command=self.login)
        back_button = tk.Button(self, text="Back", command=self.back)

        name_entry.focus_set()

        name_label.pack()
        name_entry.pack()
        password_label.pack()
        password_entry.pack()
        submit_button.pack()
        back_button.pack()

    def back(self):
        print("Admin login menu closed.")
        self.controller.show_page(ScanUserPage)

    def login(self, event=None):
        name = self.name.get()
        password = self.password.get()
        admin = Admin(name, password)

        try:
            name = admin.getName()
        except KeyError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(AdminLoginPage)
        else:
            if not admin.logged_in:
                print("Wrong password")
                # go to admin login menu
            else:
                print("Admin " + name + " has logged in.")
                self.controller.show_page(AdminMenuPage, admin)


class AdminMenuPage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.unbind('<Return>')

        self.admin = admin

        self.createGraphics()

    def createGraphics(self):
        add_user_button = tk.Button(self, text="add a user", command=self.addUser)
        remove_user_button = tk.Button(self, text="remove a user", command=self.removeUser)
        add_admin_button = tk.Button(self, text="add an admin", command=self.addAdmin)
        remove_admin_button = tk.Button(self, text="remove an admin", command=self.removeAdmin)
        add_balance_button = tk.Button(self, text="add balance to a user", command=self.addBalance)
        add_barcode_button = tk.Button(self, text="add a product barcode", command=self.addBarcode)
        remove_barcode_button = tk.Button(self, text="remove a product barcode", command=self.removeBarcode)
        back_button = tk.Button(self, text="Back", command=self.back)

        add_user_button.grid(row=0, column=0, pady=1)
        remove_user_button.grid(row=0, column=1, pady=1)
        add_admin_button.grid(row=1, column=0, pady=1)
        remove_admin_button.grid(row=1, column=1, pady=1)
        add_barcode_button.grid(row=2, column=0, pady=1)
        remove_barcode_button.grid(row=2, column=1, pady=1)
        add_balance_button.grid(row=3, column=0, pady=1)
        back_button.grid(row=4, column=0, pady=1)

    def back(self):
        print("Admin " + self.admin.getName() + " logged out.")
        self.controller.show_page(ScanUserPage)

    def addUser(self):
        self.controller.show_page(AddUserPage, self.admin)

    def removeUser(self):
        self.controller.show_page(RemoveUserPage, self.admin)

    def addAdmin(self):
        self.controller.show_page(AddAdminPage, self.admin)

    def removeAdmin(self):
        self.controller.show_page(RemoveAdminPage, self.admin)

    def addBalance(self):
        self.controller.show_page(AddBalancePage, self.admin)

    def addBarcode(self):
        self.controller.show_page(AddBarcodePage, self.admin)

    def removeBarcode(self):
        self.controller.show_page(RemoveBarcodePage, self.admin)


class AddUserPage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.addUser)

        self.admin = admin

        self.new_name = tk.StringVar()  # the name of the new user
        self.new_email = tk.StringVar()  # the email of the new user

        self.createGraphics()

    def createGraphics(self):
        name_label = tk.Label(self, text="Username of the new user")
        name_entry = tk.Entry(self, textvariable=self.new_name)

        email_label = tk.Label(self, text="E-mail of the new user")
        email_entry = tk.Entry(self, textvariable=self.new_email)

        submit_button = tk.Button(self, text="Submit", command=self.addUser)
        back_button = tk.Button(self, text="Back", command=self.back)

        name_label.pack()
        name_entry.pack()
        email_label.pack()
        email_entry.pack()
        submit_button.pack()
        back_button.pack()

    def back(self):
        self.controller.show_page(AdminMenuPage, self.admin)

    def addUser(self, event=None):
        new_name = self.new_name.get()
        new_email = self.new_email.get()

        try:
            self.admin.addUser(new_name, new_email)
        except ValueError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(AddUserPage, self.admin)
        else:
            print("User added!\tName: " + new_name + " | E-mail: " + new_email)
            self.controller.show_page(AdminMenuPage, self.admin)


class RemoveUserPage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.removeUser)

        self.admin = admin

        self.remove_name = tk.StringVar()  # the name of the user that will get removed

        self.createGraphics()

    def createGraphics(self):
        remove_label = tk.Label(self, text="Which user would you like to remove?")
        remove_entry = tk.Entry(self, textvariable=self.remove_name)

        submit_button = tk.Button(self, text="Submit", command=self.removeUser)
        back_button = tk.Button(self, text="Back", command=self.back)

        remove_label.pack()
        remove_entry.pack()
        submit_button.pack()
        back_button.pack()

    def back(self):
        self.controller.show_page(AdminMenuPage, self.admin)

    def removeUser(self, event=None):
        remove_name = self.remove_name.get()

        try:
            remove_name, email, balance, total = self.admin.removeUser(remove_name)
        except KeyError as error1:
            print(error1)
            self.controller.show_page(RemoveUserPage, self.admin)
        except ValueError as error2:
            print(error2)
            self.controller.show_page(RemoveUserPage, self.admin)
        else:
            print("User removed!\tName: " + remove_name + " | E-mail: " + email + " | Balance: " + str(balance) +
                  " kr | Total spent: " + str(total) + " kr")
            self.controller.show_page(AdminMenuPage, self.admin)


class AddAdminPage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.addAdmin)

        self.admin = admin

        self.new_name = tk.StringVar()  # the name of the new admin
        self.new_password = tk.StringVar()  # the password of the new admin

        self.createGraphics()

    def createGraphics(self):
        name_label = tk.Label(self, text="Username of the new admin")
        name_entry = tk.Entry(self, textvariable=self.new_name)

        password_label = tk.Label(self, text="Password of the new admin")
        password_entry = tk.Entry(self, textvariable=self.new_password, show="*")

        submit_button = tk.Button(self, text="Submit", command=self.addAdmin)
        back_button = tk.Button(self, text="Back", command=self.back)

        name_label.pack()
        name_entry.pack()
        password_label.pack()
        password_entry.pack()
        submit_button.pack()
        back_button.pack()

    def back(self):
        self.controller.show_page(AdminMenuPage, self.admin)

    def addAdmin(self, event=None):
        new_name = self.new_name.get()
        new_password = self.new_password.get()

        try:
            self.admin.addAdmin(new_name, new_password)
        except ValueError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(AddAdminPage, self.admin)
        else:
            print("Admin added!\tName: " + new_name)
            self.controller.show_page(AdminMenuPage, self.admin)


class RemoveAdminPage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.removeAdmin)

        self.admin = admin

        self.remove_name = tk.StringVar()  # the name of the admin that will get removed

        self.createGraphics()

    def createGraphics(self):
        remove_label = tk.Label(self, text="Which admin would you like to remove?")
        remove_entry = tk.Entry(self, textvariable=self.remove_name)

        submit_button = tk.Button(self, text="Submit", command=self.removeAdmin)
        back_button = tk.Button(self, text="Back", command=self.back)

        remove_label.pack()
        remove_entry.pack()
        submit_button.pack()
        back_button.pack()

    def back(self):
        self.controller.show_page(AdminMenuPage, self.admin)

    def removeAdmin(self, event=None):
        remove_name = self.remove_name.get()

        try:
            remove_name = self.admin.removeAdmin(remove_name)
        except KeyError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(RemoveAdminPage, self.admin)
        else:
            print("Admin removed!\tName: " + remove_name)
            self.controller.show_page(AdminMenuPage, self.admin)


class AddBalancePage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.addBalance)

        self.admin = admin

        self.name = tk.StringVar()  # the name of the user which balance will be edited
        self.added_amount = tk.StringVar()  # the amount that will be added

        self.createGraphics()

    def createGraphics(self):
        name_label = tk.Label(self, text="Username of the user")
        name_entry = tk.Entry(self, textvariable=self.name)

        amount_label = tk.Label(self, text="Amount to be added")
        amount_entry = tk.Entry(self, textvariable=self.added_amount)

        submit_button = tk.Button(self, text="Submit", command=self.addBalance)
        back_button = tk.Button(self, text="Back", command=self.back)

        name_label.pack()
        name_entry.pack()
        amount_label.pack()
        amount_entry.pack()
        submit_button.pack()
        back_button.pack()

    def back(self):
        self.controller.show_page(AdminMenuPage, self.admin)

    def addBalance(self, event=None):
        name = self.name.get()
        added_amount = self.added_amount.get()

        try:
            self.admin.addBalance(name, float(added_amount))
        except KeyError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(AddBalancePage, self.admin)
        else:
            print("Money added to balance!\tName: " + name + " | Amount: " + str(added_amount) + " kr")
            self.controller.show_page(AdminMenuPage, self.admin)


class AddBarcodePage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.addBarcode)

        self.admin = admin

        self.new_barcode = tk.StringVar()  # the barcode of the new product
        self.new_name = tk.StringVar()  # the name of the new product
        self.new_price = tk.StringVar()  # the price of the new product

        self.createGraphics()

    def createGraphics(self):
        barcode_label = tk.Label(self, text="Barcode of the product")
        barcode_entry = tk.Entry(self, textvariable=self.new_barcode)

        name_label = tk.Label(self, text="Name of the new product")
        name_entry = tk.Entry(self, textvariable=self.new_name)

        price_label = tk.Label(self, text="Price of the new product")
        price_entry = tk.Entry(self, textvariable=self.new_price)

        submit_button = tk.Button(self, text="Submit", command=self.addBarcode)
        back_button = tk.Button(self, text="Back", command=self.back)

        barcode_label.pack()
        barcode_entry.pack()
        name_label.pack()
        name_entry.pack()
        price_label.pack()
        price_entry.pack()
        submit_button.pack()
        back_button.pack()

    def back(self):
        self.controller.show_page(AdminMenuPage, self.admin)

    def addBarcode(self, event=None):
        new_barcode = self.new_barcode.get()
        new_name = self.new_name.get()
        new_price = self.new_price.get()

        try:
            self.admin.addProduct(new_barcode, new_name, float(new_price))
        except ValueError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(AddBarcodePage, self.admin)
        else:
            print("Product barcode added!\tBarcode: " + new_barcode + " | Name: " + new_name + " | Price: " +
                  str(new_price) + " kr")
            self.controller.show_page(AdminMenuPage, self.admin)


class RemoveBarcodePage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.removeBarcode)

        self.admin = admin

        self.remove_barcode = tk.StringVar()  # the barcode of the product that will get removed

        self.createGraphics()

    def createGraphics(self):
        remove_label = tk.Label(self, text="Which product would you like to remove?")
        remove_entry = tk.Entry(self, textvariable=self.remove_barcode)

        submit_button = tk.Button(self, text="Submit", command=self.removeBarcode)
        back_button = tk.Button(self, text="Back", command=self.back)

        remove_label.pack()
        remove_entry.pack()
        submit_button.pack()
        back_button.pack()

    def back(self):
        self.controller.show_page(AdminMenuPage, self.admin)

    def removeBarcode(self, event=None):
        remove_barcode = self.remove_barcode.get()

        try:
            remove_barcode, remove_name, remove_price = self.admin.removeProduct(remove_barcode)
        except KeyError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(RemoveBarcodePage, self.admin)
        else:
            print("The product " + remove_name + " with the barcode " + remove_barcode + " and price " +
                  str(remove_price) + " was successfully removed.")
            print("Product barcode removed!\tBarcode: " + remove_barcode + " | Name: " + remove_name + " | Price: "
                  + str(remove_price) + " kr")
            self.controller.show_page(AdminMenuPage, self.admin)


if __name__ == "__main__":
    # start logging of everything that gets printed to the terminal
    sys.stdout = Logger("saves/log.txt")
    sys.stderr = sys.stdout

    # start the GUI
    testObj = Windows(ScanUserPage)
    testObj.mainloop()
