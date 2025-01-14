from dotenv import load_dotenv
import os
import requests
from typing import Literal, get_args

load_dotenv()

atm_username = os.getenv("ATM_USERNAME_PROD")
atm_password = os.getenv("ATM_PASSWORD_PROD")
auth_url = os.getenv("AUTH_URL")
summary_url = os.getenv("SUMMARY_URL")
interchange_url = os.getenv("INTERCHANGE_URL")
p_buyrate = float(os.getenv("P_BUYRATE"))
a_buyrate = float(os.getenv("A_BUYRATE"))
a_name = os.getenv("A_NAME")
b_buyrate = float(os.getenv("B_BUYRATE"))
b_name = os.getenv("B_NAME")

headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Connection': 'Keep-Alive'
}

payload = {
  'CompanyID': '10',
  'Username': atm_username,
  'Password': atm_password,
  'B1': 'Login'
}

# These report IDs were pulled from the network tab when running the report in a browser
reports = {
  "Monthly": "289278",
  "Quarterly": "289362",
  "Prince": "282534",
  "Roberts": "212997",
  "Interchange": "AAD1B3B5-0616-E611-9D13-D4AE52896C06"
}

interchange_GUIDs = {
  "A": "AAD1B3B5-0616-E611-9D13-D4AE52896C06",
  "B": "769ED80B-C20A-E511-809A-D4AE52896C05"
}

# Helper functions
def round_to_quarter(x):
  return round(x * 4) / 4

# Define report Names and IDs
_REPORTS = Literal["Monthly", "Quarterly", "Prince", "Roberts"]

def get_commission_data(report_: _REPORTS = "Monthly"):
  options = get_args(_REPORTS)
  assert report_ in options, f"'{report_}' is not in {options}"
  session = requests.Session()
  # This line is run twice due to a strange way the target site handles logins
  session.post(auth_url, headers = headers, data = payload)
  session.post(auth_url, headers = headers, data = payload)

  report_params = {
    'ReportCmd': 'CustomCommand',
    'DeferQuery': 'false',
    '%24lr_override': 'true',
    'ReportID': reports[report_], 
    'CustomCmdList': 'OpenCSVBrowser'
  }

  summary = session.get(summary_url, params = report_params)
  return summary

def get_interchange_data():
  session = requests.Session()
  session.post(auth_url, headers = headers, data = payload)
  session.post(auth_url, headers = headers, data = payload)

  interchange_params = {
    'ReportCmd': 'CustomCommand',
    'DeferQuery': 'false',
    '%24lr_override': 'true',
    'ReportGUID': '',
    'CustomCmdList': 'OpenCSVBrowser'
  }

  interchange_totals = {
    "A": {
      "trx": 0,
      "interchange": 0,
      "print_as": a_name,
      "payout": 0
    },
    "B": {
      "trx": 0,
      "strx": 0,
      "interchange": 0,
      "print_as": b_name,
      "payout": 0
    }
  }

  businesses = list(interchange_GUIDs.keys())

  # Current layout of the scraped data is as follows:
  # 0 - TID, 1 - Location, 2 - Total TRX, 3 - Total Interchange (Company A)
  # 0 - TID, 1 - Location, 2 - Total TRX, 3 - Surcharge TRX, 4 - Total Interchange (Company B)
  for business in businesses:
    interchange_params["ReportGUID"] = interchange_GUIDs[business]
    results = session.get(interchange_url, params = interchange_params)

    raw_lines = results.text.splitlines()
    for raw_line in raw_lines[1:]:
      unsplit_line = raw_line[1:-1]
      line = unsplit_line.split('","')
      trx = int(line[2].replace(',', ''))
      interchange_totals[business]["trx"] += trx
      # This is not very dry, refactor when time permits
      # Payout structure is different for different businesses
      if business == "B":
        strx = int(line[3].replace(',', ''))
        interchange = float(line[4].replace('$', '').replace(',', ''))
        interchange_totals[business]["strx"] += strx
      else:
        interchange = float(line[3].replace('$', '').replace(',', ''))
      interchange_totals[business]["interchange"] += interchange
      if business == "B":
        payout = round_to_quarter(interchange_totals[business]["strx"] * b_buyrate)
      else:
        payout = interchange_totals[business]["interchange"] - (interchange_totals[business]["trx"] * (p_buyrate + a_buyrate))
      interchange_totals[business]["payout"] = payout

  return interchange_totals
  