import os
import shutil
import time
import datetime
import tarfile
import math
import boto
from filechunkio import FileChunkIO

DB_HOST = 'localhost'
DB_USER = 'root'
DB_USER_PASSWORD = 'SUYSOCSQL$521'
#DB_NAME = '/backup/dbnames.txt'
DB_NAME = ['opochmmy_enin_web','opochmmy_ensg_web','opochmmy_int_web','opochmmy_wpblog','socxoBlog','socxo_campaigns','socxo_enin_live']
BACKUP_PATH = '/backup/s3'
SourcePath = '/var/www/socxo'
tmp = '/tmp/'
DATETIME = time.strftime('%m%d%Y-%H%M%S')
TODAYBACKUPPATH = DATETIME
#Tmp = temp+TODAYBACKUPPATH
#def tmpFolder():
#	if not os.path.exists(temp):
#		os.makedirs(temp)
def removeOldbackup(path):
    os.chdir(path)
    for filename in os.listdir(path):
        if filename.endswith('.tar') or filename.endswith('.sql'):
            os.unlink(filename)
        elif  os.path.isfile(filename):
            os.remove(filename)
        else:
            shutil.rmtree(filename)
def createBkupFolder(location):
    print "creating backup folder"
    os.chdir(location)
    if not os.path.exists(TODAYBACKUPPATH):
        os.makedirs(TODAYBACKUPPATH)
def creatingDbBackup():
    os.chdir(tmp)
    for db in DB_NAME:
       dumpcmd = "mysqldump -u " + DB_USER + " --password='"+DB_USER_PASSWORD+"'" " " + db + " > " + db + ".sql"
       os.system(dumpcmd)
       shutil.move(db+".sql",TODAYBACKUPPATH)
       #os.unlink(db+".sql")
def make_tarfile(output_filename, source_dir):
    tarfile = "tar -czvf" + output_filename + ".tar"+ " " + source_dir
    os.system(tarfile)
def folderBkup():
    os.chdir(tmp)
    #os.chdir(TODAYBACKUPPATH)
    shutil.copytree(SourcePath,TODAYBACKUPPATH+"_SocxoWebsite")
    make_tarfile("Socxo_"+TODAYBACKUPPATH,TODAYBACKUPPATH+"_SocxoWebsite")
    shutil.move("Socxo_"+TODAYBACKUPPATH+".tar",TODAYBACKUPPATH)
    shutil.rmtree(TODAYBACKUPPATH+"_SocxoWebsite")
    make_tarfile(TODAYBACKUPPATH+"websiteAndDb",TODAYBACKUPPATH)
    shutil.move(TODAYBACKUPPATH+"websiteAndDb.tar",BACKUP_PATH)
def movetoS3(PATH):
    os.chdir(PATH)
    c = boto.connect_s3()
    b = c.get_bucket('socxo-backup')
    for filename in os.listdir(PATH):
        # Get file info
        source_size = os.stat(filename).st_size

        # Create a multipart upload request
        mp = b.initiate_multipart_upload(os.path.basename(filename))

    # Use a chunk size of 50 MiB (feel free to change this)
        chunk_size = 52428800
        chunk_count = int(math.ceil(source_size / float(chunk_size)))

    # Send the file parts, using FileChunkIO to create a file-like object
    # that points to a certain byte range within the original file. We
    # set bytes to never exceed the original file size.
        for i in range(chunk_count):
            offset = chunk_size * i
            bytes = min(chunk_size, source_size - offset)
            with FileChunkIO(filename, 'r', offset=offset,bytes=bytes) as fp:
                mp.upload_part_from_file(fp, part_num=i + 1)

        # Finish the upload
        mp.complete_upload()
def main():
#    tmpFolder()
    os.chdir(BACKUP_PATH)
    removeOldbackup(BACKUP_PATH)
    createBkupFolder(tmp)
    creatingDbBackup()
    folderBkup()
    movetoS3(BACKUP_PATH)
    removeOldbackup(tmp)
if __name__ == '__main__':
    main()
