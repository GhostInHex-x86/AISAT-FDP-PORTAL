from config import DRIVE_FOLDER_ID
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from services.auth_service import get_google_credentials


def upload_to_drive(file_path, filename):
    drive_service = build(
        "drive",
        "v3",
        credentials=get_google_credentials()
    )

    file_metadata = {
        "name": filename,
        "parents": [DRIVE_FOLDER_ID]
    }

    media = MediaFileUpload(
        file_path,
        resumable=True,
        mimetype=None
    )

    try:
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()
    except Exception as e:
        raise RuntimeError(
            f"Google Drive upload failed: {e}"
        )

    file_id = uploaded_file["id"]
    return f"https://drive.google.com/file/d/{file_id}/view"
