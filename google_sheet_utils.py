def set_column_width(service, spreadsheet_id, start_column, end_column, width):
    requests = [
        {
            'updateDimensionProperties': {
                'range': {
                    # 'sheetId': service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()['sheets'][0]['properties']['sheetId'],
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': start_column,
                    'endIndex': end_column + 1  # Adding 1 to include the end column
                },
                'properties': {'pixelSize': width},
                'fields': 'pixelSize'
            }
        }
    ]
    body = {'requests': requests}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    print(f"Set column width for columns {start_column} to {end_column} to {width} pixels.")

def set_wrap_text(service, spreadsheet_id, start_column, end_column):
    requests = [
        {
            'repeatCell': {
                'range': {
                    # 'sheetId': service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()['sheets'][0]['properties']['sheetId'],
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1048576,
                    'startColumnIndex': start_column,
                    'endColumnIndex': end_column + 1  # Adding 1 to include the end column
                },
                'cell': {'userEnteredFormat': {'wrapStrategy': 'WRAP'}},
                'fields': 'userEnteredFormat.wrapStrategy'
            }
        }
    ]
    body = {'requests': requests}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    print(f"Set 'wrap text' property for columns {start_column} to {end_column}.")

def write_and_highlight_values(service, spreadsheet_id, values):
    # Find the last row dynamically
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="A:A"
    ).execute()
    
    last_row = len(result.get('values', [])) + 1

    # Highlight the added rows with yellow background
    requests = [
        {
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': last_row,
                    'endRowIndex': last_row + len(values) ,
                    'startColumnIndex': 0,
                    'endColumnIndex': 1
                },
                'cell': {'userEnteredFormat': {'backgroundColor': {'red': 1, 'green': 1, 'blue': 0}}},
                'fields': 'userEnteredFormat.backgroundColor'
            }
        }
    ]

    body = {'requests': requests}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    # Write new values to the last row
    body = {
        'values': values
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"A{last_row + 1}",
        valueInputOption="RAW",
        body=body
    ).execute()

    print(f"Values {values} added to the last row in column A and highlighted with yellow.")