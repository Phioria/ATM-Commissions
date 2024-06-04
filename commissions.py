import json
from os import system, name, path, makedirs
from gatherdata import getCommissionData
from typing import Literal, get_args
from datetime import datetime

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
    #     "trx_mult": numeric,
    #     "sur_mult": numeric,
    #     "print_as": string
    #   },
    # }
    with open("json/monthly.json", "r") as file:
        atm_list = json.load(file)
        file.close()
  
    summary = getCommissionData("Monthly")
    # 0 - TID, 1 - Group, 2 - Location, 3 - Garbage, 4 - Surcharge TRX, 5 - Surcharge Amount, 6 - Transaction Volume
    lines_temp = summary.text.splitlines()
    commission_data = dict()

    # Parse each line
    # 1. Remove the first and last character of the line (which is a quotation mark)
    # 2. Split the line up into a list(array) based on the delimiter "," which prevents bad splitting on multi group locations
    # 3. Append the line list into the lines list for later use
    for line_temp in lines_temp[1:]:
        unsplit_line = line_temp[1:-1]
        line = unsplit_line.split('","')
        tid = line[0]
        loc = line[2]
        trx = int(line[4].replace(',', ''))
        sur = float(line[5].replace('$', '').replace(',', ''))
        vol = float(line[6].replace('$', '').replace(',', ''))
        commission_data[tid] = {
            "location": loc,
            "transactions": trx,
            "surcharge": sur,
            "volume": vol
        }
    returned_tids = list(commission_data.keys())
    tids = list(atm_list.keys())

    def calculateCommission(terminal):
        t_multiplier = atm_list[terminal]['trx_mult']
        s_multiplier = atm_list[terminal]['sur_mult']
        cur_loc = atm_list[terminal]["print_as"]
        cur_trx = commission_data[terminal]["transactions"]
        cur_sur = commission_data[terminal]["surcharge"]
        commission = (cur_trx * t_multiplier) + (cur_sur * s_multiplier)
        comm_obj = {
            "location": cur_loc,
            "transactions": cur_trx,
            "surcharge": cur_sur,
            "commission": commission
        }
        return comm_obj

    commissions = dict()

    for tid in tids:
        if tid in returned_tids:
            current_commission = calculateCommission(tid)
            commissions[tid] = current_commission
    commissions["Prince"] = getGroupTotal("Prince")
    commissions["Roberts"] = getGroupTotal("Roberts")
    # Todo Write this function next
    formatCommissions(commissions)
    
def getGroupTotal(group):
    summary = getCommissionData(group)
    lines_temp = summary.text.splitlines()
    lines = list()
    for line in lines_temp:
        unsplit_line = line[1:-1]
        line_list = unsplit_line.split('","')
        lines.append(line_list)
    trx_total = 0
    volume_total = 0
    for line in lines[1:]: # Skip the first line with headers
        trx = float(line[4].replace('$', '').replace(',', ''))
        volume = float(line[5].replace('$', '').replace(',', ''))
        trx_total += trx
        volume_total += volume

    with open("json/groups.json", "r") as file:
        group_details = json.load(file)
        file.close()

    t_multiplier, offset, print_as = group_details[group].values()
    commission = (trx_total * t_multiplier) - offset
    comm_obj = {
        "location": print_as,
        "transactions": trx_total,
        "surcharge": 0,
        "commission": commission
    }
    return comm_obj

_PERIOD = Literal["Monthly", "Quarterly"]

def formatCommissions(commissions, period_: _PERIOD = "Monthly"):
    options = get_args(_PERIOD)
    assert period_ in options, f"{period_} is not in {options}"
    outputDirectory = period_ + "Commissions"
    filename = period_.lower() + "-commissions-" + datetime.now().strftime("%B-%Y") + ".txt"
    filepath = path.join(outputDirectory, filename)

    # Sort the commission dictionary by location name
    # items() returns tuples of a key and value, so item[1] would be the nested dictionary
    # and item[1]['location'] would reference a value in the nested dictionary associated with the key 'location'
    sortedCommissions = dict(sorted(commissions.items(), key=lambda item:item[1]['location']))

    tids = list(sortedCommissions.keys())

    totalCommissions = 0

    # Build the output file content line by line for each location
    message = ""
    for tid in tids:
        location = sortedCommissions[tid]["location"]
        unformattedPayout = sortedCommissions[tid]["commission"]
        totalCommissions += unformattedPayout
        payout = "${:.2f}".format(unformattedPayout)
        current_str = location + ", " + payout + "\n"
        message += current_str

    if not path.exists(outputDirectory):
        makedirs(outputDirectory)
    with open(filepath, "w") as file:
        file.write(message)
        file.close()

    print(f"{period_} Commissions Complete")

if __name__ == "__main__":
    main()
