"""
Shows basic usage of the Apps Script API.
Call the Apps Script API to create a new script project, upload a file to the
project, and log the script's URL to the user.
"""
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build
import code2generateReport
from google.oauth2 import service_account
# import upload_move_files_google_drive

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/script.projects",
    "https://www.googleapis.com/auth/script.deployments",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.scripts",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/script.triggers.readonly",
    "https://www.googleapis.com/auth/script.projects",
    "https://www.googleapis.com/auth/spreadsheets"
  ]

def run(sheet_id, new_candidate_folder_id, invoice_folder_id, file_name):
  report_script_id = ""
  invoice_script_id = ""
  app_script_function_name = "createNewGoogleDocs"
  
  """Calls the Apps Script API."""
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "app_script_credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  try:
    # service = build("script", "v1", credentials=creds)
    service = build("script", "v1", credentials=creds)
    
    report_request = {
        'function': app_script_function_name,  # Replace with the name of your function
        'parameters':[sheet_id, new_candidate_folder_id, file_name],
        'devMode': False
    }

    report_response = service.scripts().run(scriptId=report_script_id, body=report_request).execute()
    print("********************************************* this is the response of generation the report template using appscript *************************************")
    if 'error' in report_response:
      print(f"Error: {report_response['error']['message']}")
    else:
      print(f"Success: {report_response['response']}")

    invoice_request = {
      'function': app_script_function_name,  # Replace with the name of your function
      'parameters':[sheet_id, invoice_folder_id],
      'devMode': False
    }
    invoice_response = service.scripts().run(scriptId=invoice_script_id, body=invoice_request).execute()
    print("********************************************* this is the response of generation the invoice template using appscript *************************************")
    if 'error' in invoice_response:
      print(f"Error: {invoice_response['error']['message']}")
    else:
      print(f"Success: {invoice_response['response']}")
  except errors.HttpError as error:
    print(error.content)