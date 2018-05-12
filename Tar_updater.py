import regex as re
import os
import tarfile
from bs4 import BeautifulSoup
import shutil

def extract(tar_url, extract_path='.'):
    tar = tarfile.open(tar_url, 'r')
    for item in tar:
        if (os.path.isdir(os.path.join(extract_path, item.name))):
            continue;
        tar.extract(item, extract_path)
        if item.name.find(".tgz") != -1 or item.name.find(".tar") != -1:
            extract(item.name, "./" + item.name[:item.name.rfind('/')])

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def create_new_tar():
    currentpath = os.getcwd()
    print("Extracting tar files")
    extract(currentpath + '/PlayerInfoXMLs/PlayerInfo.tar.gz', currentpath + "/PlayerInfoXMLs/NewPlayers")
    print("Generating new tar file")
    make_tarfile(currentpath + '/PlayerInfoXMLs/PlayerInfo.tar.gz', currentpath + "/PlayerInfoXMLs/NewPlayers/")
    print("Deleting extracted files")
    shutil.rmtree(currentpath + "/PlayerInfoXMLs/NewPlayers")
    print("Creating new folder")
    os.mkdir(currentpath + "/PlayerInfoXMLs/NewPlayers")

#create_new_tar()