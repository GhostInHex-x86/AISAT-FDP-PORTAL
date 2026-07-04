from config import SPREADSHEET_ID
from googleapiclient.discovery import build
from services.auth_service import get_google_credentials


def append_submission(row):
    sheets = build(
        "sheets",
        "v4",
        credentials=get_google_credentials()
    )

    body = {"values": [row]}
    try:
        sheets.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="Sheet1!A:I",
            valueInputOption="RAW",
            body=body
        ).execute()
    except Exception as e:
        raise RuntimeError(
            f"Google Sheets append failed: {e}"
        )
