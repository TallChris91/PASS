import tarfile
import os

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

make_tarfile('C:/Users/Chris/Documents/Syncmap/Promotie/PASS/NewInfoXMLs/PlayerInfo.tar.gz', 'C:/Users/Chris/Documents/Syncmap/Promotie/PASS/NewInfoXMLs/PlayerInfo/')