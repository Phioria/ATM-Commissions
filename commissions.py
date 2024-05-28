import json
from os import system, name
from gatherdata import gatherData

def main():
    lastError = ""
    while True:
        clearScreen()
        if lastError != "":
            print(lastError)
        printMenu()
        try:
            choice = int(input("What would you like to process?  "))
        except:
            lastError = "Please choose a numeric option."
            continue
        if choice < 1 or choice > 2:
            lastError = "Please choose a valid choice."
            continue
        if choice == 1:
            getMonthlyCommissions()
            break
        elif choice == 2:
            break
        else:
            "Invalid option. Please choose a number between 1 and 2."
    input("Press Enter to Exit")
        

def printMenu():
    menuOptions = {
        1: 'Monthly Commissions',
        2: 'Exit'
    }
    for key in menuOptions.keys():
        print(key, '--', menuOptions[key])

def clearScreen():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


def getMonthlyCommissions():
    print("Processing Monthly Commissions")
    # json expected structure
    # {
    #   "TID": {
    #       "trx_mult": numeric,
    #       "sur_mult": numeric,
    #       "print_as": string
    #   },
    # }
    #with open("json/monthly.json", "r") as file:
    #    atm_list = json.load(file)
    #    file.close()
    
    summary = gatherData()
    print(summary.text.splitlines())
    
    

if __name__ == "__main__":
    main()
