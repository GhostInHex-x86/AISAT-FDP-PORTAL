import os
from datetime import datetime
from flask_login import current_user
from werkzeug.utils import secure_filename
from services.drive_service import upload_to_drive
from services.sheets_service import append_submission
from services.cache_service import cache_submission
from services.logging_service import logger
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER


def process_submission(request):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    logger.info("[+] SUBMISSION")

    for key, value in request.form.items():
        logger.info(f"{key}: {value}")

    certificate = request.files.get("certificate")

    if certificate:
        extension = os.path.splitext(
            secure_filename(certificate.filename)
        )[1].lower()
        if extension.lower() not in ALLOWED_EXTENSIONS:
            logger.exception(
                "Invalid file type. Only PDF, JPG, JPEG, and PNG are allowed.")
            raise ValueError(
                "Invalid file type. Only PDF, JPG, JPEG, and PNG are allowed.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{current_user.username}_{request.form['program_type']}_{timestamp}{extension}"
        save_path = os.path.join(UPLOAD_FOLDER, new_filename)
        certificate.save(save_path)

        logger.info(f"\nSaved File: {new_filename}")
        logger.info(f"\nSaved Path: {save_path}")

        # Upload to Google Drive
        drive_link = upload_to_drive(save_path, new_filename)
        logger.info(f"\nUploaded to Google Drive: {drive_link}")

        # Append to Google Sheets
        sheet_data = [current_user.username,
                      request.form["program_name"],
                      request.form["program_type"],
                      request.form["organizer"],
                      request.form["venue"],
                      request.form["start_date"],
                      request.form["end_date"],
                      timestamp,
                      drive_link]
        append_submission(sheet_data)
        logger.info("\nGoogle Sheets updated successfully.")

        # os.remove(save_path) for local backup not removing the files
        # Cache the submission in the local SQLite database
        cache_submission(sheet_data)

    logger.info("[+] SUBMISSION END")
