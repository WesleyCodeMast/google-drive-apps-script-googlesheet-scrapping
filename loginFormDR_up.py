import requests
import base64
import json
from datetime import datetime, timedelta
import csv
from io import StringIO

eamil = ""
password = ""

backend_base_url = ""

def login_formDr():
    login_url = ""
    session = requests.Session()
    candidates_infos = []
    response = session.get(login_url)
    auth_token = ''
    try:
        if response.status_code == 200:
            payload = {
                'email': eamil,
                'password': password,
                'rememberDevice': True,
                'sixDigitCode': None,
                'emailSecurityCode': None,
                'deviceUuid': '',
                'rememberedDevice': {
                    'key': None,
                    'token': 'B0-moyuPKN'
                }
            }
            api_login_url = ""
            response = session.post(api_login_url, data=payload)
            
            response_data = json.loads(response.text)
            
            access_token = response_data.get('accessToken', '')

            device_info = response_data.get('deviceInfo', {})

            deviceUuid = device_info.get('deviceUuid', '')
            token = device_info.get('token')

            header, payload_base64, signature = access_token.split('.')
            auth_token = access_token
            # Replace characters in base64 encoding and decode
            payload_bytes = base64.urlsafe_b64decode(payload_base64 + '=' * (4 - len(payload_base64) % 4))

            # Convert the decoded payload to ASCII string
            payload_str = payload_bytes.decode('ascii')

            # Parse the JSON payload
            payload = json.loads(payload_str)

            iat = payload['iat']
            exp = payload['exp']

            return {
                'token': access_token,
                'payload': payload,
                'iat': iat,
                'exp': exp
            }

            if(iat and exp and (exp - iat > 0)):

                # Set up the Authorization header
                headers = {
                    'Authorization': 'Bearer ' + access_token
                }

                fetch_my_user_url = backend_base_url + "/api/submissions?page=1&dateRange=last_90_days&search=&lastPage=false&itemsPerPage=20"

                response = session.get(fetch_my_user_url, headers=headers)
                
                if response.status_code == 200:
                    response_text = json.loads(response.text)

                    response_datas = response_text.get('data', {})

                    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

                    for data in response_datas:
                        created_at = data.get('createdAt', '')
                        parsed_date = datetime.strptime(created_at, date_format)

                        current_time = datetime.utcnow()

                        ten_minutes_before = current_time - timedelta(days=5)

                        if parsed_date > ten_minutes_before:
                            info = {
                                'id': data.get('id'), 
                                'practiceId': data.get('practiceId'),
                                'recordId': data.get('recordId'),
                                'patientName': data.get('patientName'),
                                'phone': data.get('phone'),
                                'email': data.get('email'),
                                'createdAt': data.get('createdAt')
                            }

                            candidates_infos.append(info)

                            
                    print('Request successful!')
                    # Process the response content as needed
                else:
                    print('Request failed. Status code:', response.status_code)

        return {
            'auth_token': auth_token,
            'session': session, 
            'candidates_infos':candidates_infos
            }
    except BaseException:
        return  []
    

def upload_csv_pdf_to_driver(auth_token, session, candidates_infos):
    for candidate in candidates_infos:
        base_url = 'https://prod-api.formdr.com/api/submissions/' + str(candidate.get('id'))
        pdf_url = base_url + '/pdf?events=false'
        csv_url = base_url + '/csv'
        headers = {
            'Authorization': 'Bearer ' + auth_token
        }
        csv_response = session.post(csv_url, headers=headers)

        if(csv_response.status_code == 200):

            csv_content = csv_response.content

            csv_detail = csv_content.decode('utf-8')
            csv_reader = csv.DictReader(StringIO(csv_detail))

            agency_field = "Full Name of Hiring Agency:"
            position_field = "Applying for what position?"
            # Iterate through rows and find the value in the custom field
            for row in csv_reader:
                if agency_field in row:
                    agency_field_value = row[agency_field]
                    # Assuming you want to print the value in the custom field
                    print(f"{agency_field}: {agency_field_value}")
                    break
                else:
                    print(f"Custom field '{agency_field}' not found in CSV.")

                if position_field in row:
                    position_field_value = row[position_field]
                    # Assuming you want to print the value in the custom field
                    print(f"{position_field}: {position_field_value}")
                    break
                else:
                    print(f"Custom field '{position_field}' not found in CSV.")
        else:
            print(f'Failed to retrieve PDF. Status code: {csv_response.status_code}')

# results = login_formDr()

# session = results.get('session')
# candidates_infos = results.get('candidates_infos')
# auth_token = results.get('auth_token')

# print(candidates_infos)

# upload_csv_pdf_to_driver(auth_token, session, candidates_infos)