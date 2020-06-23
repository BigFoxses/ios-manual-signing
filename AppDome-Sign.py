import argparse
import re
import zipfile
from collections import OrderedDict
from contextlib import contextmanager
from json import load as json_load
from os import listdir, walk, chdir, getcwd, remove
from os.path import isdir, join, exists, relpath, realpath, basename, splitext, abspath
from shutil import rmtree, move
from subprocess import Popen, PIPE
from sys import stderr as sys_stderr
from tempfile import mkdtemp

PRIVATE_SIGNIPA_SCRIPT_NAME = splitext(basename(__file__))[0] + ".py"

ENTITLEMENTS_METADATA_SUFFIX = ".metadata"


def entitlements_path_to_metadata_path(entitlements_path):
    return splitext(entitlements_path)[0] + ENTITLEMENTS_METADATA_SUFFIX


def private_sign_ipa_run_command(cmd, _stdin=None, _stdout=None, _stderr=None):
    try:
        private_sign_ipa_log(" ".join(map(str,cmd)))
        return Popen(cmd, stdin=_stdin, stdout=_stdout, stderr=_stderr)
    except OSError as error:
        if isinstance(cmd, list):
            cmd = cmd[0]
        if error.errno == 13:
            message = "No permission to run %s" % (cmd,)
            private_sign_ipa_die_with_error(message)
        elif error.errno == 2:
            message = "Can't find %s" % (cmd,)
            private_sign_ipa_die_with_error(message)
        else:
            message = "Unknown error running %s Error: %s." % (cmd, error)
            private_sign_ipa_die_with_error(message)
    except ValueError as error:
        if isinstance(cmd, list):
            cmd = cmd[0]
        message = "Invalid arguments when trying to run %s ErrorMessage: %s" % (cmd, error)
        private_sign_ipa_die_with_error(message)
    except TypeError as error:
        if isinstance(cmd, list):
            cmd = cmd[0]
        message = "Unknown error running %s. Error: %s." % (cmd, error)
        private_sign_ipa_die_with_error(message)


def private_sign_ipa_die_with_error(error_message, return_value=-1):
    sys_stderr.write("ERROR: " + error_message)
    sys_stderr.write("\n")
    exit(return_value)


def private_sign_ipa_log(log_str):
    print("INFO: " + log_str)


@contextmanager
def private_sign_ipa_erased_temp_dir():
    temp_dir = mkdtemp()
    try:
        yield temp_dir
    except Exception as e:
        private_sign_ipa_die_with_error(str(e))
    finally:
#        rmtree(temp_dir, ignore_errors=True)
         private_sign_ipa_log("tmp_dir")


class PrivateSignZipHandler(object):
    def __init__(self, zip_path, output):
        with zipfile.ZipFile(zip_path, 'r') as zip_handler:
            zip_handler.extractall(output)
            self.files_dict = self._create_files_dict(zip_handler)

    def _create_files_dict(self, zip_handler):
        res = OrderedDict()
        for file_name in zip_handler.namelist():
            res[file_name] = zip_handler.getinfo(file_name).compress_type
        return res

    def zip_back_and_close(self, folder, output):
        old_dir = getcwd()
        chdir(folder)

        with zipfile.ZipFile(output, 'w') as zip_handler:
            for root, dirs, files in walk(realpath(folder)):
                for dir_name in dirs:
                    rel_path = relpath(join(root, dir_name))
                    zip_handler.write(rel_path, compress_type=zipfile.ZIP_STORED)

                for file_name in files:
                    rel_path = relpath(join(root, file_name))
                    compression = self.files_dict[rel_path] if rel_path in self.files_dict else zipfile.ZIP_DEFLATED
                    zip_handler.write(rel_path, compress_type=compression)

        chdir(old_dir)


def parse_args():
    parser = argparse.ArgumentParser(description='Auto-DEV iOS signing script')
    parser.add_argument("SourceIPA", help="To be inserted automatically by bash script")
    parser.add_argument("-o", "--output", help='Path of output file (file name included)', required=True)
    parser.add_argument('-s', '--signer', help="String to use as signer identity", required=True)
    return parser.parse_args()


class PrivateSignIpa(object):
    entitlements_regex = re.compile(r'entitlements_(.*)\.plist$')

    def __init__(self, signer, sha1_fingerprint=None, signing_directory=None):
        self.signer = signer
        self.sha1_fingerprint = sha1_fingerprint
        self.signing_directory = signing_directory

    def generate_codesign_cmd(self, entitlements, target):
        return ["codesign", "-v", "-f", "-s", self.signer, "--entitlement", entitlements, target]

    def validate_metadata(self, entitlements_path, executable_path):
        if self.sha1_fingerprint is None:
            return
        entitlements_metadata_path = entitlements_path_to_metadata_path(entitlements_path)
        if not exists(entitlements_metadata_path):
            return

        with open(entitlements_metadata_path) as metadata_file:
            provisioning_profile_metadata = json_load(metadata_file)
            if provisioning_profile_metadata and len(provisioning_profile_metadata) > 0 and self.sha1_fingerprint not in provisioning_profile_metadata:
                message = "The input certificate doesn't match the provisioning profile.\nValid certificates are:\n%s"%\
                          ('\n'.join(['Cert: [%s], with fingerprint: [%s]' % (cert_name, fingerprint) for (fingerprint, cert_name) in provisioning_profile_metadata.items()]), )
                private_sign_ipa_die_with_error(message)
        remove(entitlements_metadata_path)
        if self.signing_directory:
            private_sign_ipa_log("Successfully matched provisioning profile with signing identity for executable %s" %
                                 (relpath(executable_path, self.signing_directory),))

    def sign_sub_folders(self, folder):
        total_files_signed = 0

        files_list = listdir(folder)
        for dir_name in [file_name for file_name in files_list if isdir(join(folder, file_name))]:
            dir_path = join(folder, dir_name)
            total_files_signed += self.sign_sub_folders(dir_path)

        for file_name in [file_name for file_name in files_list if not isdir(join(folder, file_name))]:
            match_obj = self.entitlements_regex.match(file_name)
            if match_obj:
                executable_to_sign = join(folder, match_obj.group(1))
                if exists(executable_to_sign):
                    entitlements_path = join(folder, file_name)
                    self.validate_metadata(entitlements_path, executable_to_sign)
                    with private_sign_ipa_erased_temp_dir() as temp_entitlements_dir:
                        temp_entitlements_path = join(temp_entitlements_dir, file_name)
                        move(entitlements_path, temp_entitlements_path)
                        self.sign(executable_to_sign, temp_entitlements_path)
                        total_files_signed += 1
        return total_files_signed

    def sign(self, target, entitlements):
        try:
            p = private_sign_ipa_run_command(self.generate_codesign_cmd(entitlements, target))
            if self.signing_directory:
                private_sign_ipa_log("About to sign [%s] using codesign" % (relpath(target, self.signing_directory),))
            p.communicate()
            res = p.returncode
            if res != 0:
                raise Exception("codesign failed with error code: " + str(res))

        except Exception as e:
            private_sign_ipa_die_with_error("Failed to execute codesign with error: " + str(e))


def validate_cert(identity):
    p = private_sign_ipa_run_command(["security", "find-identity", "-v", "-p", "codesigning"], _stdin=PIPE, _stdout=PIPE, _stderr=PIPE)
    output, err = p.communicate()
    rc = p.returncode

    re_expression_certs = re.compile(r'^\s*\d+\)\s+([0-9a-fA-F]+)\s+"(.*)"')
    keychain_certs = {}
    if rc != 0 or not output:
        return None
    if type(output) == bytes:
        output = output.decode("utf-8")
    split_output = output.split("\n")
    for line in split_output:
        match = re_expression_certs.match(line)
        if match:
            groups = match.groups()
            keychain_certs[groups[0]] = groups[1]

    keychain_certs_fingerprint_list = keychain_certs.keys()
    keychain_cert_name_list = keychain_certs.values()
    if len(identity) == 40 and identity in keychain_certs_fingerprint_list:
        signing_cert_fingerprint = identity
        private_sign_ipa_log("Successfully matched certificate SHA-1 fingerprint [%s] in keychain" %
                             (signing_cert_fingerprint,))
    else:
        matching_fingerprints_by_name = [fingerprint for fingerprint, name in keychain_certs.items() if name == identity]
        if len(matching_fingerprints_by_name) > 1:
            private_sign_ipa_die_with_error(
                "The keychain identity you have used matches more than one certificate, please use the SHA-1 fingerprint instead. available fingerprints for this certificate name are:\n%s" % (
                    "\n".join(matching_fingerprints_by_name)))
        if len(matching_fingerprints_by_name) < 1:
            private_sign_ipa_die_with_error(
                "The identity: %s was not found in the keychain.\nValid identities by name are:\n%s\nValid identitys by sha-1 are:\n%s\n" % (
                    identity, "\n".join(keychain_cert_name_list), "\n".join(keychain_certs_fingerprint_list)))
        signing_cert_fingerprint = matching_fingerprints_by_name[0]
        private_sign_ipa_log("Successfully matched signing identity [%s] to SHA-1 fingerprint [%s] in keychain" %
                             (identity, signing_cert_fingerprint))
    return signing_cert_fingerprint


def main():
    script_args = parse_args()

    signing_cert_fingerprint = validate_cert(script_args.signer)
    with private_sign_ipa_erased_temp_dir() as temp_dir:
        zip_handler = PrivateSignZipHandler(script_args.SourceIPA, temp_dir)
        ps = PrivateSignIpa(script_args.signer, signing_cert_fingerprint, temp_dir)
        ps.sign_sub_folders(temp_dir)
        zip_handler.zip_back_and_close(temp_dir, abspath(script_args.output))
        private_sign_ipa_log("Signed ipa output file location:\n ===> %s <===" % (abspath(script_args.output, )))


if __name__ == "__main__":
    main()