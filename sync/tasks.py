import subprocess

import boto3
from celery import shared_task
from decouple import config

DB_NAME = config("DATABASE_URL")

BACKUP_PATH = config("BACKUP_PATH")

FILENAME_PREFIX = 'mgh.backup'

# Amazon S3 settings.
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = 'nanoafrika'


@shared_task
def backup():
    filename = 'sync_backup'

    destination = r'%s/%s' % (BACKUP_PATH, filename)

    print('Backing up %s database to %s' % (DB_NAME, destination))
    ps = subprocess.Popen(
        ['pg_dump', DB_NAME, '-f', destination],
        stdout=subprocess.PIPE
    )
    output = ps.communicate()[0]
    for line in output.splitlines():
        print(line)

    print('Uploading %s to Digital ocean spaces...' % filename)
    upload_to_s3(destination, filename)


def upload_to_s3(source_path, destination_filename):
    """
    Upload a file to an AWS S3 bucket.
    """
    # new
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='ams3',
                            endpoint_url='https://ams3.digitaloceanspaces.com',
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    client.upload_file(source_path,  # Path to local file
                       'nanoafrika',  # Name of Space
                       destination_filename)  # Name for remote file
