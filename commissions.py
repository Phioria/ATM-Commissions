import json
from os import system, name, path, makedirs, listdir, remove
from shutil import copy
from gatherdata import get_commission_data, get_interchange_data
from typing import Literal, get_args
from datetime import datetime

def main():
    last_error = ""
    while True:
        clear_screen()
        if last_error != "":
            print(last_error)
        print_menu()
        try:
            choice = int(input("What would you like to process?  "))
        except:
            last_error = "Please choose a numeric option."
            continue
        if choice < 1 or choice > 6:
            last_error = "Please choose a valid choice."
            continue
        if choice == 1:
            get_monthly_commissions()
            break
        elif choice == 2:
            get_interchange()
            break
        elif choice == 3:
            #get_quarterly_commissions()
            break
        elif choice == 4:
            get_monthly_commissions()
            get_interchange()
            collect_files()
            break
        elif choice == 5:
            get_monthly_commissions()
            get_interchange()
            #get_quarterly_commissions()
            collect_files()
            break
        elif choice == 6:
            break
        else:
            "Invalid option. Please choose a number between 1 and 2."
    input("Press Enter to Exit")
        

# Helper Functions
def print_menu():
    menu_options = {
        1: 'Monthly Commissions',
        2: 'Interchange',
        3: 'Quarterly Commissions',
        4: 'Monthey Commissions and Interchange',
        5: 'Everything',
        6: 'Exit'
    }
    for key in menu_options.keys():
        print(key, '--', menu_options[key])

def clear_screen():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def get_current_month_year():
    return datetime.now().strftime("%B-%Y")

def write_or_append_totals(category, amount):
    summary_directory = "Summary"
    filename = "summary-" + get_current_month_year() + ".txt"
    filepath = path.join(summary_directory, filename)
    formatted_amount = "${:.2f}".format(amount)
    with open(filepath, "a") as file:
        file_string = category + ": " + formatted_amount + "\n"
        file.write(file_string)
        file.close()

def write_string_to_file(name, data):
    with open(name, "w") as file:
        file.write(data)
        file.close()

def collect_files():
    cc_directory = "CurrentCommissions"
    comm_directory = "MonthlyCommissions"
    int_directory = "Interchange"
    summary_directory = "Summary"

    # Remove old file from the CurrentCommissions directory
    try:
        files = listdir(cc_directory)
        for file in files:
            file_path = path.join(cc_directory, file)
            if path.isfile(file_path):
                remove(file_path)
        print("Got rid of the clutter. Ready for file collection")
    except OSError:
        print("Oops, boss...something bad happened while trying to delete old files ¯\_(ツ)_/¯")

    # Copy current Summary file to CurrentCommissions directory
    try:
        summary_file = "summary-" + get_current_month_year() + ".txt"
        summary_file_path = path.join(summary_directory, summary_file)
        new_summary_file_path = path.join(cc_directory, summary_file)
        if path.isfile(summary_file_path):
            copy(summary_file_path, new_summary_file_path)
    except OSError:
        print("The current summary file is being uncooperative and unmovable")

    # Copy current Commission file to CurrentCommissions directory
    try:
        commission_file = "monthly-commissions-" + get_current_month_year() + ".txt"
        commission_file_path = path.join(comm_directory, commission_file)
        new_commission_file_path = path.join(cc_directory, commission_file)
        if path.isfile(commission_file_path):
            copy(commission_file_path, new_commission_file_path)
    except OSError:
        print("The current commission file is being uncooperative and unmovable")

    # Copy current Interchange file to CurrentCommissions directory
    try:
        interchange_file = "interchange-" + get_current_month_year() + ".txt"
        interchange_file_path = path.join(int_directory, interchange_file)
        new_interchange_file_path = path.join(cc_directory, interchange_file)
        if path.isfile(interchange_file_path):
            copy(interchange_file_path, new_interchange_file_path)
    except OSError:
        print("Interchange file doesn't want to copy")

    # If it is a quarterly month, then copy the quarterly commission file as well
    if datetime.now().month % 3 == 1:
        quarterly_directory = "QuarterlyCommissions"
        try:
            quarterly_file = "quarterly-commissions-" + get_current_month_year() + ".txt"
            quarterly_file_path = path.join(quarterly_directory, quarterly_file)
            new_quarterly_file_path = path.join(cc_directory, quarterly_file)
            if path.isfile(quarterly_file_path):
                copy(quarterly_file_path, new_quarterly_file_path)
        except OSError:
            print("Quarterly file doesn't want to be copied")
    print("Got the gang back together")


def get_monthly_commissions():
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
  
    summary = get_commission_data("Monthly")
    # 0 - TID, 1 - Group, 2 - Location, 3 - Garbage, 4 - Surcharge TRX, 5 - Surcharge Amount, 6 - Transaction Volume
    lines_temp = summary.text.splitlines()
    commission_data = dict()

    # Parse each line
    # 1. Remove the first and last character of the line (which is a quotation mark)
    # 2. Split the line up into a list based on the delimiter "," which prevents bad splitting on multi group locations
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

    def calculate_commission(terminal):
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
            current_commission = calculate_commission(tid)
            commissions[tid] = current_commission
    commissions["Prince"] = get_group_total("Prince")
    commissions["Roberts"] = get_group_total("Roberts")
    format_commissions(commissions)
    
def get_group_total(group):
    summary = get_commission_data(group)
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

def format_commissions(commissions, period_: _PERIOD = "Monthly"):
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

def get_interchange():
    print("Processing Interchange")
    interchange_totals = get_interchange_data()

    total_interchange = sum(d["payout"] for d in interchange_totals.values() if d)

    write_or_append_totals("Interchange", total_interchange)
    message = format_interchange(interchange_totals)

    interchange_directory = "Interchange"
    filename = "interchange-" + get_current_month_year() + ".txt"
    filepath = path.join(interchange_directory, filename)
    write_string_to_file(filepath, message)

    print("Interchange Complete")

def format_interchange(interchange):
    subs = list(interchange.keys())
    message = ""
    for sub in subs:
        location = interchange[sub]["print_as"]
        payout = "${:.2f}".format(interchange[sub]["payout"])
        current_str = location + ", " + payout + "\n"
        message += current_str
    return message

if __name__ == "__main__":
    main()
