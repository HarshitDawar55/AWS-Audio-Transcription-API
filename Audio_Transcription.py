# Importing the required libraries
from flask import Flask, request, jsonify
from utilitties import (
    upload_audio_file_to_s3,
    transcribe_audio_file,
    download_transcript_from_s3,
)
from datetime import datetime

# Defining the App with the Name
app = Flask(__name__)


# Creating a error handler for the Internal Server Error
@app.errorhandler(500)
def error_505(error):
    return "There is some problem with the application!", 400


# Creating a default route to translate the text into the destination language
@app.route("/", methods=["POST"])
def transcribe():
    try:
        # Step 1: Taking the Audio File from the User through our API
        audio_file = request.files.get("audio_file")
        if audio_file is None:
            return jsonify({"message": "Blank Audio File Uploaded", "status": 400}), 400
        else:
            # Step 2: Uploading the Audio File to S3
            message, status = upload_audio_file_to_s3(audio_content=audio_file)
            if status == 200:
                # Step 3 & 4: Starting Audio File Transcription and saving that into the S3 Bucket
                transcription_message, transcription_status = transcribe_audio_file(
                    audio_filename=audio_file.filename,
                    job_name=datetime.now().strftime("%d-%m-%Y_%H-%M-%S"),
                )
                if transcription_status == 200:
                    # Step 5: Downloading the Transcription of the Audio File from S3
                    download_message, download_status = download_transcript_from_s3(
                        filename=audio_file.filename
                    )
                    if download_status == 200:
                        # Step 6: Returning the Transcribed content to the user
                        return (
                            jsonify({"message": download_message, "status": 200}),
                            200,
                        )
                    else:
                        return (
                            jsonify(
                                {
                                    "message": download_message,
                                    "status": download_status,
                                }
                            ),
                            400,
                        )
                else:
                    return (
                        jsonify(
                            {
                                "message": transcription_message,
                                "status": transcription_status,
                            }
                        ),
                        400,
                    )
            else:
                return jsonify({"message": message, "status": status}), 400
    except Exception as e:
        print(str(e))


# Running the app on port 80 & on any host to make it accessible through the container
app.run(host="0.0.0.0", port=80)
