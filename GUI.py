import tkinter as tk
from back_end import *
from files import *
from functools import partial


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
        admins_button = tk.Button(self, text="Admins", command=self.admins)
        users_button = tk.Button(self, text="Users", command=self.users)
        products_button = tk.Button(self, text="Products", command=self.products)
        settings_button = tk.Button(self, text="Settings", command=self.settings)
        back_button = tk.Button(self, text="Log out", command=self.back)

        admins_button.grid(row=0, column=0, pady=1, padx=1)
        users_button.grid(row=0, column=1, pady=1, padx=1)
        products_button.grid(row=1, column=0, pady=1, padx=1)
        settings_button.grid(row=1, column=1, pady=1, padx=1)
        back_button.grid(row=4, column=0, pady=1, padx=1)

    def back(self):
        print("Admin " + self.admin.getName() + " has logged out.")
        self.controller.show_page(ScanUserPage)

    def admins(self):
        self.controller.show_page(AdminsPage, self.admin)

    def users(self):
        self.controller.show_page(UsersPage, self.admin)

    def products(self):
        self.controller.show_page(ProductsPage, self.admin)

    def settings(self):
        self.controller.show_page(SettingsPage, self.admin)


class AdminsPage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.unbind('<Return>')

        self.admin = admin

        self.canvas = tk.Canvas(self, borderwidth=0)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.createGraphics()

    def onFrameConfigure(self, event):
        # Reset the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def createGraphics(self):
        tk.Button(self.frame, text="Back", command=self.back).grid(row=0, column=0)
        tk.Button(self.frame, text="add an admin", command=self.addAdmin).grid(row=0, column=1)
        tk.Button(self.frame, text="Change my Password",
                  command=partial(self.change_password)).grid(row=0, column=2)

        admins = self.admin.getAllAdmins()
        i = 1
        for name in admins:
            tk.Label(self.frame, text=name).grid(row=i, column=0)
            tk.Button(self.frame, text="Remove", command=partial(self.remove, name)).grid(row=i, column=1)
            i += 1

    def back(self):
        self.controller.show_page(AdminMenuPage, self.admin)

    def change_password(self):
        self.controller.show_page(ChangePasswordPage, self.admin)

    def remove(self, name):
        self.controller.show_page(RemoveAdminPage, self.admin, name)

    def addAdmin(self):
        self.controller.show_page(AddAdminPage, self.admin)


class ChangePasswordPage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.changePassword)

        self.admin = admin

        self.old_password = tk.StringVar()
        self.new_password = tk.StringVar()

        self.createGraphics()

    def createGraphics(self):
        tk.Label(self, text="Input your current password.").pack()
        tk.Entry(self, textvariable=self.old_password, show="*").pack()

        tk.Label(self, text="Input your new password.").pack()
        tk.Entry(self, textvariable=self.new_password, show="*").pack()

        tk.Button(self, text="Submit", command=self.changePassword).pack()
        tk.Button(self, text="Back", command=self.back).pack()

    def back(self):
        self.controller.show_page(AdminsPage, self.admin)

    def changePassword(self, event=None):
        old_password = self.old_password.get()
        new_password = self.new_password.get()

        if self.admin.checkPassword(old_password):
            self.admin.changePassword(new_password)
            print(self.admin.getName() + "'s password was successfully changed.")
            self.back()
        else:
            print("The password of the admin was not correct.")
            self.controller.show_page(ChangePasswordPage, self.admin)


class RemoveAdminPage(tk.Frame):
    def __init__(self, parent, controller, admin, name):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.removeAdmin)

        self.admin = admin

        self.name = name  # the name of the admin that will get removed
        self.name_check = tk.StringVar()  # name input that will check against the name

        self.createGraphics()

    def createGraphics(self):
        tk.Label(self, text="Are you sure you would like to remove " + self.name + "?\n" 
                            "To make sure that you are not making a mistake, input the name " + self.name +
                            " below.").pack()
        tk.Entry(self, textvariable=self.name_check).pack()

        tk.Button(self, text="Submit", command=self.removeAdmin).pack()
        tk.Button(self, text="Back", command=self.back).pack()

    def back(self):
        self.controller.show_page(AdminsPage, self.admin)

    def removeAdmin(self, event=None):
        remove_name = self.name_check.get()

        if remove_name == self.name:
            try:
                remove_name = self.admin.removeAdmin(remove_name)
            except KeyError as error1:
                print(error1)
                self.controller.show_page(RemoveAdminPage, self.admin, self.name)
            except ValueError as error2:
                print(error2)
                self.controller.show_page(RemoveAdminPage, self.admin, self.name)
            else:
                print("Admin removed!\tName: " + remove_name)

                # if the admin removed them self they need to get logged out
                if remove_name == self.admin.getName():
                    self.controller.show_page(ScanUserPage)
                else:
                    self.back()
        else:
            print("The names did not match.")
            self.controller.show_page(RemoveAdminPage, self.admin, self.name)


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
        self.controller.show_page(AdminsPage, self.admin)

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


class UsersPage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.unbind('<Return>')

        self.admin = admin

        self.canvas = tk.Canvas(self, borderwidth=0)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.createGraphics()

    def onFrameConfigure(self, event):
        # Reset the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def createGraphics(self):
        tk.Button(self.frame, text="Back", command=self.back).grid(row=0, column=0)
        tk.Button(self.frame, text="add a user", command=self.addUser).grid(row=0, column=1)

        users = self.admin.getAllUsers()

        i = 1  # creating a row of buttons above, so we start on the second row i.e. row=1
        for name in users:
            # There is a pseudo user called admin, we don't want to show that one
            if not name == "admin":
                balance = users[name]["balance"]
                email = users[name]["email"]
                total = users[name]["total"]
                text = name + " | E-mail: " + email + " | Balance: " + str(balance) + " | Total expenses: " + str(total)
                tk.Label(self.frame, text=text).grid(row=i, column=0)
                tk.Button(self.frame, text="View history", command=partial(self.viewHistory, name)).grid(row=i, column=1)
                tk.Button(self.frame, text="Add balance", command=partial(self.addBalance, name)).grid(row=i, column=2)
                tk.Button(self.frame, text="Remove", command=partial(self.removeUser, name)).grid(row=i, column=3)
            i += 1

    def back(self):
        self.controller.show_page(AdminMenuPage, self.admin)

    def addUser(self):
        self.controller.show_page(AddUserPage, self.admin)

    def viewHistory(self, name):
        self.controller.show_page(ViewHistoryPage, self.admin, name)

    def addBalance(self, name):
        self.controller.show_page(AddBalancePage, self.admin, name)

    def removeUser(self, name):
        self.controller.show_page(RemoveUserPage, self.admin, name)


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
        self.controller.show_page(UsersPage, self.admin)

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
            self.back()


class RemoveUserPage(tk.Frame):
    def __init__(self, parent, controller, admin, name):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.removeUser)

        self.admin = admin

        self.name = name  # the name of the user that will get removed
        self.name_check = tk.StringVar()  # name input that will check against the name

        self.createGraphics()

    def createGraphics(self):
        tk.Label(self, text="Are you sure you would like to remove " + self.name + "?\n" 
                            "To make sure that you are not making a mistake, input the name " + self.name +
                            " below.").pack()
        tk.Entry(self, textvariable=self.name_check).pack()

        tk.Button(self, text="Submit", command=self.removeUser).pack()
        tk.Button(self, text="Back", command=self.back).pack()

    def back(self):
        self.controller.show_page(UsersPage, self.admin)

    def removeUser(self, event=None):
        remove_name = self.name_check.get()

        if remove_name == self.name:
            try:
                remove_name, email, balance, total = self.admin.removeUser(remove_name)
            except KeyError as error1:
                print(error1)
                self.controller.show_page(RemoveUserPage, self.admin, self.name)
            except ValueError as error2:
                print(error2)
                self.controller.show_page(RemoveUserPage, self.admin, self.name)
            else:
                print("User removed!\tName: " + remove_name + " | E-mail: " + email + " | Balance: " + str(balance) +
                      " kr | Total spent: " + str(total) + " kr")
                self.back()
        else:
            print("The names did not match.")
            self.controller.show_page(RemoveUserPage, self.admin, self.name)


class AddBalancePage(tk.Frame):
    def __init__(self, parent, controller, admin, name):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.addBalance)

        self.admin = admin

        self.name = name  # the name of the user which balance will be edited
        self.added_amount = tk.StringVar()  # the amount that will be added

        self.createGraphics()

    def createGraphics(self):
        tk.Label(self, text="How much would you like to add to " + self.name + "'s balance?").pack()
        tk.Entry(self, textvariable=self.added_amount).pack()

        tk.Button(self, text="Submit", command=self.addBalance).pack()
        tk.Button(self, text="Back", command=self.back).pack()

    def back(self):
        self.controller.show_page(UsersPage, self.admin)

    def addBalance(self, event=None):
        added_amount = self.added_amount.get()

        try:
            self.admin.addBalance(self.name, float(added_amount))
        except KeyError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(AddBalancePage, self.admin)
        else:
            print("Money added to balance!\tName: " + self.name + " | Amount: " + str(added_amount) + " kr")
            self.back()


class ViewHistoryPage(tk.Frame):
    def __init__(self, parent, controller, admin, name):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.unbind('<Return>')

        self.admin = admin

        self.name = name

        self.canvas = tk.Canvas(self, borderwidth=0)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.createGraphics()

    def onFrameConfigure(self, event):
        # Reset the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def createGraphics(self):
        tk.Button(self.frame, text="Back", command=self.back).grid(row=0, column=0)

        user = User(self.name)
        history = user.getHistory()

        # these are all lists of the historic events
        timestamp = history["time"]
        name = history["name"]
        action = history["action"]
        barcode = history["barcode"]
        product_name = history["product name"]
        amount = history["amount"]

        for i in range(len(timestamp)):  # can use the length of any of the lists
            # need to use row=i+1 since we already created a button in row 0
            tk.Label(self.frame, text=timestamp[i]).grid(row=i+1, column=0)
            tk.Label(self.frame, text=name[i]).grid(row=i + 1, column=1)
            tk.Label(self.frame, text=action[i]).grid(row=i + 1, column=2)
            tk.Label(self.frame, text=barcode[i]).grid(row=i + 1, column=3)
            tk.Label(self.frame, text=product_name[i]).grid(row=i + 1, column=4)
            tk.Label(self.frame, text=amount[i]).grid(row=i + 1, column=5)

    def back(self):
        self.controller.show_page(UsersPage, self.admin)


class ProductsPage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.unbind('<Return>')

        self.admin = admin

        self.canvas = tk.Canvas(self, borderwidth=0)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.createGraphics()

    def onFrameConfigure(self, event):
        # Reset the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def createGraphics(self):
        tk.Button(self.frame, text="Back", command=self.back).grid(row=0, column=0)
        tk.Button(self.frame, text="Add a Product", command=self.addProduct).grid(row=0, column=1)

        products = self.admin.getAllProducts()

        i = 1  # creating a row of buttons above, so we start on the second row i.e. row=1
        for barcode in products:
            # There is a pseudo product with the barcode 000 that we do not want to print
            if not barcode == "000":
                price = products[barcode]["price"]
                name = products[barcode]["name"]
                text = "Barcode : " + barcode + " | Name: " + name + " | Price: " + str(price)
                tk.Label(self.frame, text=text).grid(row=i, column=0)
                tk.Button(self.frame, text="Change Name", command=partial(self.changeName, barcode)).grid(row=i, column=1)
                tk.Button(self.frame, text="Change price", command=partial(self.changePrice, barcode)).grid(row=i, column=2)
                tk.Button(self.frame, text="Remove", command=partial(self.removeProduct, barcode)).grid(row=i, column=3)
            i += 1

    def back(self):
        self.controller.show_page(AdminMenuPage, self.admin)

    def addProduct(self):
        self.controller.show_page(AddProductPage, self.admin)

    def changeName(self, barcode):
        self.controller.show_page(ChangeProductNamePage, self.admin, barcode)

    def changePrice(self, barcode):
        self.controller.show_page(ChangeProductPricePage, self.admin, barcode)

    def removeProduct(self, barcode):
        self.controller.show_page(RemoveProductPage, self.admin, barcode)


class AddProductPage(tk.Frame):
    def __init__(self, parent, controller, admin):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.addProduct)

        self.admin = admin

        self.new_barcode = tk.StringVar()  # the barcode of the new product
        self.new_name = tk.StringVar()  # the name of the new product
        self.new_price = tk.IntVar()  # the price of the new product

        self.createGraphics()

    def createGraphics(self):
        barcode_label = tk.Label(self, text="Barcode of the new product")
        barcode_entry = tk.Entry(self, textvariable=self.new_barcode)

        name_label = tk.Label(self, text="Name of the new product")
        name_entry = tk.Entry(self, textvariable=self.new_name)

        price_label = tk.Label(self, text="Price of the new product")
        price_entry = tk.Entry(self, textvariable=self.new_price)

        submit_button = tk.Button(self, text="Submit", command=self.addProduct)
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
        self.controller.show_page(ProductsPage, self.admin)

    def addProduct(self, event=None):
        new_barcode = self.new_barcode.get()
        new_name = self.new_name.get()
        new_price = self.new_price.get()

        try:
            self.admin.addProduct(new_barcode, new_name, new_price)
        except ValueError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(AddProductPage, self.admin)
        else:
            print("Product added!\t Barcode: " + new_barcode + "\tName: " + new_name + " | Price: " + str(new_price))
            self.back()


class ChangeProductNamePage(tk.Frame):
    def __init__(self, parent, controller, admin, barcode):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.changeName)

        self.admin = admin
        self.barcode = barcode
        product = Product(barcode)
        self.product_name = product.getName()

        self.new_name = tk.StringVar()  # the new name of the product

        self.createGraphics()

    def createGraphics(self):
        name_label = tk.Label(self, text="The new name of the product " + self.product_name)
        name_entry = tk.Entry(self, textvariable=self.new_name)

        submit_button = tk.Button(self, text="Submit", command=self.changeName)
        back_button = tk.Button(self, text="Back", command=self.back)

        name_label.pack()
        name_entry.pack()
        submit_button.pack()
        back_button.pack()

    def back(self):
        self.controller.show_page(ProductsPage, self.admin)

    def changeName(self, event=None):
        new_name = self.new_name.get()

        try:
            old_name = self.admin.updateProductName(self.barcode, new_name)
        except KeyError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(ChangeProductPricePage, self.admin)
        else:
            print("Name updated!\tBarcode: " + self.barcode + " | Old name: " +
                  str(old_name) + " | New name: " + str(new_name))
            self.controller.show_page(ProductsPage, self.admin)


class ChangeProductPricePage(tk.Frame):
    def __init__(self, parent, controller, admin, barcode):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.changePrice)

        self.admin = admin
        self.barcode = barcode
        product = Product(barcode)
        self.product_name = product.getName()

        self.new_price = tk.IntVar()  # the new price of the product

        self.createGraphics()

    def createGraphics(self):
        price_label = tk.Label(self, text="The new price of the product " + self.product_name)
        price_entry = tk.Entry(self, textvariable=self.new_price)

        submit_button = tk.Button(self, text="Submit", command=self.changePrice)
        back_button = tk.Button(self, text="Back", command=self.back)

        price_label.pack()
        price_entry.pack()
        submit_button.pack()
        back_button.pack()

    def back(self):
        self.controller.show_page(ProductsPage, self.admin)

    def changePrice(self, event=None):
        new_price = self.new_price.get()

        try:
            old_price = self.admin.updateProductPrice(self.barcode, new_price)
        except KeyError as error:
            print("An error occurred: " + str(error))
            self.controller.show_page(ChangeProductPricePage, self.admin)
        else:
            print("Price updated!\tBarcode: " + self.barcode + " | Name: " + self.product_name + " | Old price: " +
                  str(old_price) + " | New price: " + str(new_price))
            self.controller.show_page(ProductsPage, self.admin)


class RemoveProductPage(tk.Frame):
    def __init__(self, parent, controller, admin, barcode):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        controller.bind('<Return>', self.removeProduct)

        self.admin = admin

        self.barcode = barcode  # the barcode of the product that will get removed
        product = Product(barcode)
        self.product_name = product.getName()  # the name of the product
        self.barcode_check = tk.StringVar()  # barcode input that will check against the barcode

        self.createGraphics()

    def createGraphics(self):
        tk.Label(self, text="Are you sure you would like to remove " + self.barcode + " " + self.product_name + "?\n" 
                            "To make sure that you are not making a mistake, input the barcode " + self.barcode +
                            " below.").pack()
        tk.Entry(self, textvariable=self.barcode_check).pack()

        tk.Button(self, text="Submit", command=self.removeProduct).pack()
        tk.Button(self, text="Back", command=self.back).pack()

    def back(self):
        self.controller.show_page(ProductsPage, self.admin)

    def removeProduct(self, event=None):
        remove_barcode = self.barcode_check.get()

        if remove_barcode == self.barcode:
            try:
                barcode, name, price = self.admin.removeProduct(self.barcode)
            except KeyError as error1:
                print(error1)
                self.controller.show_page(RemoveUserPage, self.admin, self.barcode)
            else:
                print("Product removed!\tBarcode: " + barcode + " | Name: " + name + " | Price: " + str(price) +
                      " kr")
                self.back()
        else:
            print("The barcode did not match.")
            self.controller.show_page(RemoveUserPage, self.admin, self.barcode)


if __name__ == "__main__":
    testObj = Windows(ScanUserPage)
    testObj.mainloop()
