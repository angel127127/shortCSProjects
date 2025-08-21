import tkinter as tk
from tkinter import messagebox
import re
import hashlib
import requests

## main widget
root = tk.Tk()
root.title("Checking password strength")
root.geometry('500x375+100+100')

## hashes the password then checks if it has been found in data breaches
def pwnedCheck(password):
    ## hashes password
    hashedPass = hashlib.sha1(password.encode('utf-8')).hexdigest()
    ## api expects string in upper case
    upperHash = hashedPass.upper()
    ## only sending the first 5 characters of the hash to the api
    ## to stop the password leaving the computer and protect it
    substringSent = upperHash[:5]
    substringKeep = upperHash[5:]
    
    ## query
    url = f"https://api.pwnedpasswords.com/range/{substringSent}"
    # passList is list of all hashes starting with first 5 characters
    passList = requests.get(url)

    ## checks if response has been recieved
    if passList.status_code != 200:
        return "API error - not working :("
    ## checks if any of returned hashes matches password one
    hashes = (line.split(":") for line in passList.text.splitlines())
    for i in hashes:
        h = i[0]
        count = i[1]
        if h == substringKeep:
            return f"Password found in {count} breaches"
    return "Password not found in any data breaches"
    

## takes a string input and checks it against the regular expression, then calls the pwnedCheck function
def passChecker():
    password = entryBox.get()
    upper = bool(re.search(r"[A-Z]", password))
    lower = bool(re.search(r"[a-z]", password))
    number = bool(re.search(r"[0-9]", password))
    symbol = bool(re.search(r"[^A-Za-z0-9]", password))
    passLength = bool(len(password) >= 8)
    ## checks if the entered password matches the 5 criteria using regular expressions
    pasSum = sum([upper, lower, number, symbol, passLength])
    if pasSum == 5:
        result="Very strong password"
    elif pasSum >= 4:
        result="Strong password"
    elif pasSum >=2:
        result="Medium password, needs improvement"
    else:
        result="Weak password, needs improvement"

    pwned_res = pwnedCheck(password)

    messagebox.showinfo("Password check results", f"Strength result: {result}\nPwned check: {pwned_res}")

## attributes of main widget
textLabel = tk.Label(root, text="Enter your password to test its strength >> ")
entryBox = tk.Entry(root, show="*", width=25)
enterButton = tk.Button(root, text="Check the strength", command=passChecker,
                   activebackground="orange", bd=3)
    

## placing attributes
textLabel.place(relx=0.05, rely=0.25)
entryBox.place(relx=0.6, rely=0.25)
enterButton.place(relx=0.4, rely=0.8)

root.mainloop()
