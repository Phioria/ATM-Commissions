from dotenv import load_dotenv
import os
import requests

load_dotenv()

atm_username = os.getenv("ATM_USERNAME_PROD")
atm_password = os.getenv("ATM_PASSWORD_PROD")
auth_url = os.getenv("AUTH_URL")
#a = os.getenv("LOGIN_URL")
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


def main():
  print("ATM_USERNAME_DEV: ", atm_username)
  print("ATM_PASSWORD_DEV: ", atm_password)
  print("LOGIN_URL: ", auth_url)

def gatherData():
  session = requests.Session()
  # This line is run twice due to a strange way the target site handles logins
  session.post(auth_url, headers = headers, data = payload)
  session.post(auth_url, headers = headers, data = payload)

  report_params = {
    'ReportCmd': 'CustomCommand',
    'DeferQuery': 'false',
    '%24lr_override': 'true',
    'ReportID': '289278', # This was pulled from the network tab when running the report in a browser
    'CustomCmdList': 'OpenCSVBrowser'
  }

  summary = session.get(summary_url, params = report_params)
  return summary

if __name__ == "__main__":
  main()
