from google.oauth2 import service_account
import google.auth.transport.requests
from googleapiclient.discovery import build
import sys
import random
import csv
import io
import requests
from google.auth.transport.requests import AuthorizedSession
import os
from google.oauth2.credentials import Credentials
import app_script
import screenshot
from googleapiclient.http import MediaFileUpload
from time import sleep
from upload_download_utils import upload2drive
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google_sheet_utils import set_column_width, set_wrap_text, write_and_highlight_values

SCOPES = [
    "https://www.googleapis.com/auth/script.projects",
    'https://www.googleapis.com/auth/script.deployments',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.scripts',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/script.triggers.readonly',
    'https://www.googleapis.com/auth/script.projects',
    'https://www.googleapis.com/auth/spreadsheets'
  ]

credentials = service_account.Credentials.from_service_account_file('credential.json')

# cred = service_account.Credentials.from_service_account_file(
#     'credential.json',
#     scopes=['https://www.googleapis.com/auth/script.projects', 
#             'https://www.googleapis.com/auth/script.deployments',
#             'https://www.googleapis.com/auth/drive',
#             'https://www.googleapis.com/auth/drive.scripts',
#             'https://www.googleapis.com/auth/documents',
#             'https://www.googleapis.com/auth/script.triggers.readonly',
#             'https://www.googleapis.com/auth/script.projects',
#             'https://www.googleapis.com/auth/spreadsheets'
#         ]
# )
creds = None
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

csv_files = []
# if os.path.exists("token.json"):
#     creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# Create a Google Drive API service
service = build('drive', 'v3', credentials=creds)
sheets_service = build('sheets', 'v4', credentials=creds)
apps_script_service = build('script', 'v1', credentials=creds)

# def getAccessToken():

#     SERVICE_ACCOUNT_FILE = "credential.json" # Please set your value.

#     creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
#     creds.refresh(google.auth.transport.requests.Request())
#     return creds.token

def get_all_files(service):
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

def find_folder_id(service, folder_name):
    results = service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        return None

def get_files_in_a_folder(service, folder_id):
    results = service.files().list(q=f"'{folder_id}' in parents", pageSize=100, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found in the folder.')
    else:
        print('Files in the folder:')
        for item in items:
            print(f"{item['name']} ({item['id']})")
    return items

def get_folders_in_folder(folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
        fields="files(id, name)").execute()
    
    folders = results.get('files', [])

    return folders

def find_sub_folderId_in_folder(parent_folder_id, folder_name):

    sub_folder_id = None
    folders = get_folders_in_folder(parent_folder_id)
    for folder in folders:
        if folder['name'] == folder_name:
            sub_folder_id = folder['id']
            break

    return sub_folder_id

def create_folder(parent_id, folder_name):
    exist_folder_id = find_folder_id(service, folder_name)
    folder_metadata = {
        'name': folder_name,
        'parents': [parent_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder['id']

def move_file(service, file_id, destination_folder_id):
    file = service.files().get(fileId=file_id, fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))

    # Remove the file from the source folder
    service.files().update(fileId=file_id,
                           addParents=destination_folder_id,
                           removeParents=previous_parents,
                           fields='id, parents').execute()

    print(f"Moved file ID {file_id} to folder ID {destination_folder_id}")

    return file_id

def get_file_name(file_id):
    try:
        file_metadata = service.files().get(fileId=file_id).execute()
        return file_metadata['name']
    except Exception as e:
        print(f"Error getting file name: {e}")
        return None
    
def create_google_sheet_in_folder(parent_folder_id, sheet_title):
    # sheet_metadata = {
    #     'properties': {
    #         'title': sheet_title
    #     }
    # }

    # # Create the Google Sheet
    # sheet = sheets_service.spreadsheets().create(body=sheet_metadata).execute()
    # sheet_id = sheet['spreadsheetId']

    # # Move the Google Sheet to the custom folder
    # new_sheet_id = move_file(service, sheet_id, parent_folder_id)

    # rename_file(new_sheet_id, sheet_title)
    file_metadata = {
        'name': sheet_title,
        'parents': [parent_folder_id],
        'mimeType': 'application/vnd.google-apps.spreadsheet',
    }
    res = service.files().create(body=file_metadata).execute()
    return res.get('id')


def rename_first_sheet(spreadsheet_id, new_sheet_name):
    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet['sheets']

        if sheets:
            first_sheet_id = sheets[0]['properties']['sheetId']

            request_body = {
                "requests": [
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": first_sheet_id,
                                "title": new_sheet_name
                            },
                            "fields": "title"
                        }
                    }
                ]
            }

            response = sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()

            print(f"First sheet renamed to '{new_sheet_name}' successfully.")
        else:
            print("No sheets found in the spreadsheet.")
    except Exception as e:
        print(f"Error renaming sheet: {e}")

def rename_file(file_id, new_name):
    try:
        file_metadata = {'name': new_name}
        service.files().update(fileId=file_id, body=file_metadata).execute()
    except Exception as e:
        print(f"Error renaming file: {e}")

def create_sheet_and_import_csv(sheets_service, new_folder_id, csv_data, csv_title):
    sheet_id = create_google_sheet_in_folder(new_folder_id, csv_title)
     # Clear existing data in the sheet
    test_data=['test;this is test', 'test1;this is test2']
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=sheet_id,
        range='Sheet1',  # Update with your sheet name or range
        body={}
    ).execute()

    # Update the sheet with the CSV data
    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Sheet1',  # Update with your sheet name or range
        valueInputOption='RAW',
        body={'values': csv_data}
    ).execute()
    
    rename_first_sheet(sheet_id, 'Data')

    return sheet_id
# mary_folder_id = find_folder_id(service, mary_folder_name)

# candidate_folder_id = find_folder_id(service, candidate_folder_name)

# if mary_folder_id and candidate_folder_id:
#     mary_csv_files = service.files().list(q=f"'{mary_folder_id}' in parents and mimeType='text/csv'").execute()
#     csv_files = mary_csv_files.get('files', [])

#     for csv in csv_files:
#         csv_content = service.files().get_media(fileId=csv['id']).execute()

#         move_file(service, csv['id'], candidate_folder_id)

        # create_sheet_and_import_csv(sheets_service, candidate_folder_id, csv_content)


# get_all_files(service)

# def start(agency_folder_id, candidate_folder_id):
    
#     # files_in_agency = get_files_in_a_folder(service, agency_folder_id)
#     results = service.files().list(q=f"'{agency_folder_id}' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
#     items = results.get('files', [])
#     # Move each file to the destination folder
#     for item in items:
#         new_folderId_in_mary_report = create_folder(candidate_folder_id, item['name'])

#         files_in_item_folder = get_files_in_a_folder(service, item['id'])

#         for file in files_in_item_folder:
#             move_file(service, file['id'], new_folderId_in_mary_report)

def list_csv_files(folder_id):
    csv_files = []

    response = service.files().list(q=f"'{folder_id}' in parents", pageSize=50, fields="nextPageToken, files(id, name, mimeType)").execute()

    files = response.get('files', [])
    
    for file in files:
        if file['mimeType'] == 'text/csv':
            file_info = {
                'file_name': file['name'],
                'file_id': file['id']
            }
            csv_files.append(file_info)

        # If the file is a folder, list its contents recursively
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            csv_files.extend(list_csv_files(file['id']))

    return csv_files

def list_sheet_files(folder_id):
    sheet_files = []

    response = service.files().list(q=f"'{folder_id}' in parents", pageSize=50, fields="nextPageToken, files(id, name, mimeType)").execute()

    files = response.get('files', [])
    
    for file in files:
        if file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
            file_info = {
                'file_name': file['name'],
                'file_id': file['id']
            }
            sheet_files.append(file_info)

        # If the file is a folder, list its contents recursively
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            sheet_files.extend(list_sheet_files(file['id']))

    return sheet_files

def get_custom_val_from_csv_reader(reader, field_name):
    for row in reader:
        if field_name == row.get('sep=;').split(';')[0]:
            return row.get('sep=;').split(';')[1]

def get_csv_reader(csv_file_id):
    request = service.files().get_media(fileId=csv_file_id)
    content = request.execute()
    # Assuming the CSV has a header row, you may need to adjust the logic accordingly
    reader = csv.DictReader(io.StringIO(content.decode('utf-8')))
    
    return reader

def get_candidate_datas(file):
    reader = get_csv_reader(file.get('file_id'))
    agency_val =  get_custom_val_from_csv_reader(reader, 'Full Name of Hiring Agency:')

    depart_name = ''
    if agency_val == None:
        return None
    for a_val in agency_val.split(' '):
        if isinstance(a_val, int):
            depart_name = depart_name + a_val
        else:
            depart_name = depart_name + a_val[0]

    can_name = get_custom_val_from_csv_reader(reader, 'Full Name')

    fname = can_name.split(' ')[0] + can_name.split(' ')[1][0]
    position_val = get_custom_val_from_csv_reader(reader, 'Applying for what position?')
    
    return [str(fname) + ' ' + str(depart_name) + ' ' + str(position_val), can_name]

def signature_on_ROI(file):
    reader = get_csv_reader(file.get('file_id'))
    signatures = []
    for row in reader:
        field_name = row.get('sep=;').split(';')[0]

        if 'Signature of Client' == field_name:
            signatures.append(row.get('sep=;').split(';')[1])
    if len(signatures) > 0 and signatures[len(signatures) - 1] == "Yes":
        return True
    else:
        return False
# def upload_file_into_drive(service, file_path, folder_id = None):
#     file_metadata = {
#         'name': 'screenshot.png',
#         # 'parents': [folder_id] if folder_id else None
#     }
#     try:
#         media = MediaFileUpload(file_path, mimetype = 'image/png')

#         file = (
#             service.files()
#             .create(body=file_metadata, media_body=media, fields="id")
#             .execute()
#         )     

#         print('File ID: %s' % file.get('id'))
#         # os.remove(file_path)
#         return file.get('id')
    
#     except Exception as e:
#         print("screenshot upload is failed")
#         print(e)
#         return None
    
def get_script_id(script_name):
    try:
        # Search for the Apps Script by name
        query = f"name = '{script_name}' and mimeType = 'application/vnd.google-apps.script'"
        results = service.files().list(q=query).execute()

        # Get the script ID from the first result
        if 'files' in results and results['files']:
            script_id = results['files'][0]['id']
            print(f"Script ID for '{script_name}': {script_id}")
            return script_id
        else:
            print(f"No Apps Script found with the name '{script_name}'.")
            return None
    except Exception as e:
        print(f"Error getting script ID: {e}")
        return None

def run_apps_script(spreadsheet_id, script_property_key):
    try:
        # Retrieve the Script property value
        response = service.files().get(fileId=spreadsheet_id).execute()
        script_property_value = response.get('appProperties', {}).get(script_property_key)

        if script_property_value:
            print(f"Running Apps Script with property: {script_property_value}")
            # Implement the logic to run the script based on the property value
        else:
            print("No script property found.")
    except Exception as e:
        print(f"Error running script: {e}")

if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("Usage: python script.py <agency_name> <candidate_name>")
    #     sys.exit(1)

    # agency_name = sys.argv[1]
    # candidate_name = sys.argv[2]

    agency_name = "mhoisingtonlmft"
    # Get folder Id
    background_folder_id = find_folder_id(service, "Backgrounds")

    agency_folder_id = find_sub_folderId_in_folder(background_folder_id, agency_name)

    mary_folder_id = find_folder_id(service, "Mary Reports New")
    mhoisingtonlmft_folder_id = find_folder_id(service, agency_name)
    invoice_folder_id = find_folder_id(service, "Invoices NEW - Mary Access Only")
    csv_files_list = list_csv_files(mhoisingtonlmft_folder_id)
    
    # code_generate_report_id = get_script_id("Code To Generate Reports")
    # code_generate_report_script_property = 'CodeToGenerateReports'
    # code_generate_invoice_id = get_script_id("Code To Generate Invoice")
    # code_generate_invoice_script_property = 'CodeToGenerateInvoice'

    # report_script_id = "1HXGAw7oqkXFK0Xf7ddTi7cUY0bNIyoLp_lc2iZxBvvX81-Gkhmuw7frs"

    # Authorize the session

    # Run the function in your Apps Script


    # Print the response
    sheet_files_list = list_sheet_files(mary_folder_id)

    for csv_file in csv_files_list:
        file_id = csv_file.get('file_id')
        candidate_datas = get_candidate_datas(csv_file)
        
        new_can_folder_name = candidate_datas[0]
        
        candidate_name = candidate_datas[1]

        if new_can_folder_name == None:
            continue
        new_candidate_folder_id = create_folder(mary_folder_id, new_can_folder_name)

        signature_of_client = signature_on_ROI(csv_file)

        if signature_of_client:
            driver = screenshot.login()
            screenshot_result = screenshot.screenshot_signature(driver, candidate_name)
            if screenshot_result != None:
                upload2drive('screenshot.png', new_candidate_folder_id)
        move_file(service, file_id, new_candidate_folder_id)
        csv_content = service.files().get_media(fileId=file_id).execute()
        reader = csv.reader(csv_content.decode('utf-8').splitlines())
        csv_data = []
        # Convert CSV data to a 2D list
        # csv_data = list(reader)
        for d in csv_content.decode('utf-8').splitlines():
            csv_data.append(d.split(';'))
        csv_title = get_file_name(file_id).split('-')[1].split('.')[0]
        sheetId = create_sheet_and_import_csv(sheets_service, new_candidate_folder_id, csv_data , csv_title)
        set_column_width(sheets_service, sheetId, 0, 2, 220)
        write_and_highlight_values(sheets_service, sheetId, [['When stressed or upset'], ['Hobbies'], ['Supports']])
        set_wrap_text(sheets_service, sheetId, 0, 3)
        try:
            app_script.run(sheetId, new_candidate_folder_id, invoice_folder_id, new_can_folder_name)
        except Exception as e:
            print(e)
        
        print(new_can_folder_name)