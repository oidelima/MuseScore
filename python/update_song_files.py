import argparse
import boto3
import os
import datetime
import tempfile
import tqdm

# AWS S3 details
SONG_FILES_BUCKET_NAME = 'pianogram-songs'
SONG_FILES_BACKUPS_BUCKET_NAME = 'pianogram-songs-backups'
AWS_REGION = 'us-west-1'

MID_FILE_NAME = "song.mid"
SHEET_METADATA_FILE_NAME = "sheet.json"
SHEET_PNG_DIRNAME = "sheet"
SHEET_PNG_FILENAME = "page.png"
EXECUTABLE_FILEPATH = f"{os.getcwd()}/../builds/Win-Qt5.15.2-msvc2019_64-VS17-RelWithDebInfo/install/bin/MuseScore4.exe"

def backup_song_files(source_dir, destination_dir):
    """Backs up the song files to the destination directory"""
    os.system(f"aws s3 sync {source_dir} {destination_dir}")
    print(f"Backed up '{source_dir}' to '{destination_dir}'")

def export_mscz_to_file(source_filepath, dest_filepath):
    """Exports the mscz file to diferent file format"""
    os.system(f"{EXECUTABLE_FILEPATH} {source_filepath} -o  {dest_filepath}")

def create_sheet_metadata_from_mscz(source_filepath, dest_filepath):
    """Creates the sheet metadata file from the mscz file"""
    os.system(f"{EXECUTABLE_FILEPATH} {source_filepath} --score-meta -o  {dest_filepath}")

def get_project_mscz_file_keys(s3_client, bucket):
    """Gets the project.mscz file keys from the bucket"""
    paginator = s3_client.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=bucket)

    mscz_file_keys = []
    for response in response_iterator:
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('/project.mscz'):
                mscz_file_keys.append(obj['Key'])
    return mscz_file_keys

def create_new_song_files_from_mscz(bucket, dest_dir):  
    """Creates the new song files (song.mid, sheet.json and page-x.pngs) from the mscz files in the bucket"""
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    mscz_file_keys = get_project_mscz_file_keys(s3_client, bucket)

    print(f"Creating new song files from mscz files in destination directory: {dest_dir} ...")
    for key in tqdm.tqdm(mscz_file_keys):
        song_id, filename = key.split('/')
        
        song_dir = f"{dest_dir}\{song_id}"
        os.makedirs(song_dir, exist_ok=True)
        os.makedirs(f"{song_dir}\{SHEET_PNG_DIRNAME}", exist_ok=True)

        filepath = f"{song_dir}\{filename}"
        s3_client.download_file(bucket, key, filepath)

        export_mscz_to_file(filepath, f"{song_dir}\{MID_FILE_NAME}")
        export_mscz_to_file(filepath, f"{song_dir}\{SHEET_PNG_DIRNAME}\{SHEET_PNG_FILENAME}")
        create_sheet_metadata_from_mscz(filepath, f"{song_dir}\{SHEET_METADATA_FILE_NAME}")
        
def sync_prod_bucket_with_new_song_files(bucket, source_dir):
    """Syncs the prod bucket with the new song files"""
    os.system(f"aws s3 sync {source_dir} s3://{bucket}")
    print(f"Synced '{source_dir}' to '{bucket}'")

def main():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%m-%d-%Y_%H-%M-%S")
    backup_song_files(f"s3://{SONG_FILES_BUCKET_NAME}", f"s3://{SONG_FILES_BACKUPS_BUCKET_NAME}/{formatted_datetime}")
    temp_dir = tempfile.mkdtemp()
    create_new_song_files_from_mscz(SONG_FILES_BUCKET_NAME, temp_dir)

    update_prod_bucket = input("Do you want to update the prod bucket? (y/n): ")
    if update_prod_bucket.lower() == 'y':
        sync_prod_bucket_with_new_song_files(SONG_FILES_BUCKET_NAME, temp_dir)


    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--aws_access_key_id', type=str, help='AWS access key ID', )
    parser.add_argument('--aws_secret_access_key', type=str, help='AWS secret access key')
    
    args = parser.parse_args()
    main()



