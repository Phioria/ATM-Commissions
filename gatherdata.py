from dotenv import load_dotenv
import os
import requests

load_dotenv()

atm_username = os.getenv("ATM_USERNAME_DEV")
atm_password = os.getenv("ATM_PASSWORD_DEV")

def main():
  print("ATM_USERNAME_DEV: ", atm_username)
  print("ATM_PASSWORD_DEV: ", atm_password)

if __name__ == "__main__":
  main()
