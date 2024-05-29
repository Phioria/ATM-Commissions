from dotenv import load_dotenv
import os
import requests
from typing import Literal, get_args

load_dotenv()

atm_username = os.getenv("ATM_USERNAME_PROD")
atm_password = os.getenv("ATM_PASSWORD_PROD")
auth_url = os.getenv("AUTH_URL")
summary_url = os.getenv("SUMMARY_URL")

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
  "Roberts": "212997"
}

# Define report Names and IDs
_REPORTS = Literal["Monthly", "Quarterly", "Prince", "Roberts"]

def getCommissionData(report_: _REPORTS = "Monthly"):
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
