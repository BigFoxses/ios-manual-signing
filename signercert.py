import argparse
import re
import fnmatch
from contextlib import contextmanager
from json import load as json_load
from os import listdir, walk, chdir, getcwd, remove
from os.path import isdir, join, exists, relpath, realpath, basename, splitext, abspath
from shutil import rmtree, move
from subprocess import Popen, PIPE
from sys import stderr as sys_stderr
from tempfile import mkdtemp
import os
import zipfile



def parse_args():
    parser = argparse.ArgumentParser(description='Display APK SIGNING CERTFIFICATE Fingeprint from IPA')
    parser.add_argument('-a', '--apk', help="target APK", required=True)
    return parser.parse_args()


class ZipHandler(object):
    def __init__(self, zip_path, output):
        with zipfile.ZipFile(zip_path, 'r') as zip_handler:
            zip_handler.extractall(output)

@contextmanager
def create_erase_temp_dir():
    temp_dir = mkdtemp()
    try:
        yield temp_dir
    except Exception as e:
        apksignercert_die_with_error(str(e))
    finally:
        rmtree(temp_dir, ignore_errors=True)


def apksignercert_run_command(cmd, _stdin=None, _stdout=None, _stderr=None):
    try:
        return Popen(cmd, stdin=_stdin, stdout=_stdout, stderr=_stderr)
    except OSError as error:
        if isinstance(cmd, list):
            cmd = cmd[0]
        if error.errno == 13:
            message = "No permission to run %s" % (cmd,)
            apksignercert_die_with_error(message)
        elif error.errno == 2:
            message = "Can't find %s" % (cmd,)
            apksignercert_die_with_error(message)
        else:
            message = "Unknown error running %s Error: %s." % (cmd, error)
            apksignercert_die_with_error(message)
    except ValueError as error:
        if isinstance(cmd, list):
            cmd = cmd[0]
        message = "Invalid arguments when trying to run %s ErrorMessage: %s" % (cmd, error)
        apksignercert_die_with_error(message)
    except TypeError as error:
        if isinstance(cmd, list):
            cmd = cmd[0]
        message = "Unknown error running %s. Error: %s." % (cmd, error)
        apksignercert_die_with_error(message)

def  retreive_RSA_file(pattern, folder):
    for root, dirs, files in walk(realpath(folder)):
        for file in files:
            if fnmatch.fnmatch(file, pattern):
                yield os.path.join(root,file)
    return                 




def apksignercert_log(log_str):
    print("INFO: " + log_str)

def apksignercert_die_with_error(error_message, return_value=-1):
    sys_stderr.write("ERROR: " + error_message)
    sys_stderr.write("\n")
    exit(return_value)

def getSHA(rsa_file):
        p = apksignercert_run_command(["keytool", "-printcert", "-file", rsa_file], _stdin=PIPE, _stdout=PIPE, _stderr=PIPE)
        output, err = p.communicate()
        rc = p.returncode
        re_expression_certs = re.compile(r'^.*SHA1:(.*).*')
        if rc != 0 or not output:
            return None
        if type(output) == bytes:
            output = output.decode("utf-8")
        split_output = output.split("\n")
        for line in split_output:
            match = re_expression_certs.match(line)
            if match:
                groups = match.groups()
                return groups[0]
        apksignercert_die_with_error("NO SHA found. COMMAND OUT = %s", output)


def main():
    script_args = parse_args() 
    with create_erase_temp_dir() as temp_dir:
        zip_handler = ZipHandler(script_args.apk, temp_dir)
        for rsa_file in  retreive_RSA_file('*.RSA',temp_dir):
            sha1=getSHA(rsa_file)
            apksignercert_log("SHA1 ===> %s <===" % sha1)


if __name__ == "__main__":
    main()