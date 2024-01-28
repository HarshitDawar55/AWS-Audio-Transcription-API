import boto3
import os
import time
import json

# Defining the AWS Services clients
s3 = boto3.client(
    service_name="s3",
    region_name=os.getenv("S3_REGION"),
    aws_access_key_id=os.getenv("aws_access_key"),
    aws_secret_access_key=os.getenv("aws_secret_key"),
)

transcribe_client = boto3.client(
    service_name="transcribe",
    region_name=os.getenv("S3_REGION"),
    aws_access_key_id=os.getenv("aws_access_key"),
    aws_secret_access_key=os.getenv("aws_secret_key"),
)


def upload_audio_file_to_s3(audio_content):
    try:
        s3.put_object(
            Body=audio_content.read(),
            Bucket="harshitdawar-audio-files",
            Key=audio_content.filename,
        )
        return "File Uploaded Successfully", 200
    except Exception as e:
        print("Exception in Uploading the Audio File to S3: " + str(e))
        return "Exception in Uploading the Audio File to S3", 400


def download_transcript_from_s3(filename):
    try:
        s3.download_file(
            "harshitdawar-audio-transcriptions",
            filename,
            "./" + filename,
        )
        with open("./" + filename, "r") as f:
            content = json.loads(f.read())
        return content["results"]["transcripts"][0]["transcript"], 200
    except Exception as e:
        print("Exception in Downloading the Audio File to S3: " + str(e))
        return "Exception in Downloading the Audio File from S3", 400


def transcribe_audio_file(audio_filename, job_name):
    try:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": f"s3://harshitdawar-audio-files/{audio_filename}"},
            MediaFormat="mp3",
            LanguageCode="en-US",
            OutputBucketName="harshitdawar-audio-transcriptions",
            OutputKey=audio_filename.split(".")[0] + ".txt",
        )
        max_tries = 100
        while max_tries > 0:
            max_tries -= 1
            job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = job["TranscriptionJob"]["TranscriptionJobStatus"]
            if job_status in ["COMPLETED", "FAILED"]:
                print(f"Job {job_name} is {job_status}.")
                if job_status == "COMPLETED":
                    print(
                        f"Download the transcript from\n"
                        f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}"
                    )
                    return "Transcription Successful", 200
                else:
                    print("Audio Transcription Job Failed!")
                    return "Transcription Failed", 400
            else:
                print(f"Waiting for {job_name}. Current status is {job_status}.")
            time.sleep(10)
    except Exception as e:
        print("Exception in Transcribing the Audio File: " + str(e))
        return "Exception in Transcribing the Audio File", 400
