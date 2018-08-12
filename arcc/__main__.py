from string import Template
from argparse import ArgumentParser

import os

import pathlib
import tarfile, zipfile
import logging
import shutil

course_title = "course.sigai"
student_name = "sigai.student"
base_port = 40000

# This assumes a few things:
# 1. sigai.student<N>_id_rsa_1
#    is the private key
# 2. sigai.student<N>_id_rsa_1.ppk
#    is the putty configuration
# 3. sigai.student<N>_id_rsa_1.pub
#    is the public key
# 4. sigai.student<N>_passphrase_1.txt
#    is the passphrase file
keys_content = {
    "pem": Template("${student}.pem"),
    "ppk": Template("${student}.ppk"),
    "pub": Template("${student}.pem.pub"),
    "txt": Template("${student}_pass.txt"),
}


def main(args):
    cfg = Template(open("arcc/config", "r").read())
    
    logging.basicConfig(format="%(levelname)10s | %(message)s",
                        filename="logs/arcc.log", level=logging.DEBUG)

    logging.info("User-specified directory: {}".format(args.directory))
    
    os.chdir(pathlib.Path(args.directory))
    here = pathlib.Path(os.getcwd())
    logging.info("Now in {}".format(str(here)))
    
    ls = [pathlib.Path(x) for x in os.listdir(".") if ".tgz" in x]
    
    for key in ls:
        if course_title in str(key):
            continue
        
        logging.debug("Beginning to operate on {}".format(key))
        
        # assumes keys are given in `sigai.student<N>-key.tgz` format
        student = str(key).split("-")[0]
        
        n = int(student.replace(student_name, ""))
        port = str(base_port + n)
        
        conf = cfg.substitute(dict(student=student, port=port))
        try:
            this_tar = tarfile.open(key)
            this_tar.extractall()
            logging.debug("Extracted to {}".format(key.stem))
        except tarfile.ExtractError:
            print("Failed to extract {}".format(key))
            logging.error("Failed to extract to {}".format(key.stem))
            continue
            
        os.chdir(key.stem)
        
        contents = {k: pathlib.Path(v.substitute(dict(student=student))) for k, v in keys_content.items()}
        this_dir = [pathlib.Path(d) for d in os.listdir(".")]
        
        for file_ in this_dir:
            try:
                accepted = [".ppk", ".pub", ".txt"]
                idx = accepted.index(file_.suffix)
                # removes the period in front of the suffix
                look = accepted[idx][1:]
            except ValueError:
                look = "pem"
            
            logging.debug("\t{} -> {}".format(str(file_), str(contents[look])))
            file_.rename(contents[look])
            
        zip_ = pathlib.Path(student + ".zip")
        logging.debug("Writing zipfile `{}`".format(str(here.joinpath(zip_))))
        with zipfile.ZipFile(here.joinpath(zip_), mode="w") as zip_:
            for new in contents.values():
                try:
                    zip_.write(new)
                    logging.debug("\t\twriting {}".format(str(new)))
                except FileNotFoundError:
                    logging.error("Failed to write `{}`".format(str(new)))
            zip_.writestr("/config", conf)
            logging.debug("\t\twriting conf")
            
        os.chdir(here)
        logging.info("CLEANING UP")
        shutil.rmtree(key.stem)


if __name__ == "__main__":
    parser = ArgumentParser(description="Handles bulk-modification of files "
                                        "needed for access to the ARCC resources "
                                        "at the Institute for Simulation and "
                                        "Training at UCF.")
    
    parser.add_argument("--directory", "-d", required=True)
    
    main(parser.parse_args())
