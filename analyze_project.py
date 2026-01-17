from gdrive_mcp import get_gdrive_service
import os
import io
from googleapiclient.http import MediaIoBaseDownload

def download_file(service, file_id, file_name, dest_dir):
    print(f"Downloading {file_name} ({file_id})...")
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    
    file_path = os.path.join(dest_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(fh.getbuffer())
    print(f"Saved to {file_path}")

def main():
    service = get_gdrive_service()
    dest_dir = "temp_analysis"
    os.makedirs(dest_dir, exist_ok=True)

    # 1. Download Key Root Files
    root_files = {
        "ecs.py": "1QIbYBzEsvt7FK1WbWm3b51Xghzh5HM3k",
        "items.py": "17_KJ8kkvrE_BBkVe9JsG8RhOkCNOKMgK",
        "monster.py": "1MvHiOltMGs0cr4ketajEwblLYCm5xnIL",
        "map.py": "1PVhOXEac8plngK_GcAlqvIiBY2LE2k0I",
        "balance_tuner.py": "1wSCqgRYi3h_2oWzEtJlYA5cI9ExFSUEd",
        "inventory.py": "1gIDbxJ_9h1I_ctFcVA4xN5txTalKiOB8",
        "skills.py": "1Jgb5gNr6DOp8Um2qh5vyeUoAGyb2JuNv"
    }
    
    for name, fid in root_files.items():
        try:
            download_file(service, fid, name, dest_dir)
        except Exception as e:
            print(f"Failed to download {name}: {e}")

    # 2. Inspect and Download 'data' folder
    data_folder_id = "1HEXrmgFHh3Hykh7ACU6Ij_fiVC1QUcRO"
    print(f"\nInspecting 'data' folder ({data_folder_id})...")
    
    query = f"'{data_folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    data_files = results.get('files', [])
    
    if not data_files:
        print("'data' folder is empty.")
    else:
        print(f"Found {len(data_files)} files in 'data':")
        for f in data_files:
            print(f"- {f['name']}")
            # Download if it looks like data
            if f['name'].endswith('.csv') or f['name'].endswith('.json'):
                 download_file(service, f['id'], f['name'], dest_dir)

if __name__ == "__main__":
    main()
