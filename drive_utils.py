def find_pdf_by_name(service, folder_id, start_name):
    # Call the Drive v3 API to search for PDF files in the specified folder
    query = f"'{folder_id}' in parents and mimeType='application/pdf' and name contains '{start_name}'"
    results = service.files().list(q=query, pageSize=10, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print(f'No PDF files found in the folder with the name starting with "{start_name}".')
    else:
        print(f'PDF files in the folder with the name starting with "{start_name}":')
        for item in items:
            print(f"{item['name']} ({item['id']})")

    return items