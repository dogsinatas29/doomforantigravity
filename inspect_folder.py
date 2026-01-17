from gdrive_mcp import get_gdrive_service

def inspect_folder(folder_id):
    service = get_gdrive_service()
    
    print(f"Inspecting Folder ID: {folder_id}")
    
    # List files in the folder
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name, mimeType, size)").execute()
    files = results.get('files', [])
    
    if not files:
        print("Folder is empty or not accessible.")
    else:
        print(f"Found {len(files)} files:")
        for f in files:
            print(f"- [{f['mimeType']}] {f['name']} (ID: {f['id']}, Size: {f.get('size', 'N/A')})")

if __name__ == "__main__":
    # 'data' folder ID from previous step
    target_folder_id = "1HEXrmgFHh3Hykh7ACU6Ij_fiVC1QUcRO" 
    inspect_folder(target_folder_id)
