#!/usr/bin/env python3

# I attempted to replicate all behavior of the original script, including error
# messages and error handling, etc.
#
# - Ian Taylor

import sys
import os
import shutil
from subprocess import run
import time


TEMP_DIR = '/tmp/optical-test'
ISO_NAME = 'optical-test.iso'
SAMPLE_FILE_PATH = '/usr/share/example-content/'
SAMPLE_FILE = 'Ubuntu_Free_Culture_Showcase'
MD5SUM_FILE = 'optical_test.md5'
START_DIR = os.getcwd()
# mutable global, set after a successful mount -- used to allow for unmounting
# after an exception, during cleanup
mount_pt = None


def create_working_dirs(temp_dir=TEMP_DIR):
    '''Creates and cd's to TEMP_DIR.'''
    try:
        print("Creating Temp directory and moving there ...")

        # will throw exceptions on failure
        if not os.path.exists(temp_dir):
            os.makedir(temp_dir)
        os.chdir(temp_dir)

        print(f'Now working in {os.getcwd()} ...')
    except Exception as e:
        raise RuntimeError('Failed to create working directories') from e


def get_sample_data(sample_file_path=SAMPLE_FILE_PATH,
                    sample_file=SAMPLE_FILE,
                    temp_dir=TEMP_DIR):
    try:
        # Get our sample files
        print(f'Getting sample files from {sample_file_path} ...')
        # copy2 to preserve attributes
        # (as in previous behavior using `cp -a ...`)
        shutil.copy2(os.path.join(sample_file_path, sample_file), temp_dir)
    except Exception as e:
        raise RuntimeError('Failed to copy sample data') from e


def generate_md5(sample_file=SAMPLE_FILE):
    try:
        # Generate the md5sum
        print("Generating md5sums of sample files ...")
        cwd = os.getcwd()
        os.chdir(SAMPLE_FILE)
        md5sum_file_fullpath = os.path.join(TEMP_DIR, MD5SUM_FILE)

        run(f'md5sum -- * > {md5sum_file_fullpath}', shell=True)
        try:
            # Check the sums for paranoia sake -- throws exception for nonzero
            # return, which we do not catch until the very end of this
            # function...
            check_md5(md5sum_file_fullpath)
        finally:
            # ...but we always want to return to the previous directory, even
            # if check_md5 fails.
            os.chdir(cwd)
    except Exception as e:
        raise RuntimeError('Failed to generate initial md5') from e


def check_md5(md5sum_filepath):
    print("Checking md5sums ...")
    run(["md5sum", "-c", md5sum_filepath], check=True)


def generate_iso():
    try:
        # Generate ISO image
        print("Creating ISO Image ...")
        run(
            [
                'genisoimage',
                '-input-charset',
                'UTF-8',
                '-r',
                '-J',
                '-o',
                ISO_NAME,
                SAMPLE_FILE
            ],
            check=True
        )
    except Exception as e:
        raise RuntimeError('Failed to create ISO image') from e


def burn_iso(optical_drive, optical_type):
    try:
        # Burn the ISO with the appropriate tool
        print("Sleeping 10 seconds in case drive is not yet ready ...")
        time.sleep(10)
        print("Beginning image burn ...")
        if optical_type == 'cd':
            run(
                [
                    'wodim',
                    '-eject',
                    f'dev={optical_drive}',
                    ISO_NAME
                ],
                check=True
            )
        elif optical_type in ('dvd', 'bd'):
            run(
                [
                    'growisofs',
                    '-dvd-compat',
                    '-Z',
                    f"{optical_drive}={ISO_NAME}"
                ],
                check=True
            )
        else:
            print(f"Invalid type specified '{optical_type}'")
            sys.exit(1)
    except Exception as e:
        raise RuntimeError('Failed to burn ISO image') from e


def check_disk(optical_drive):
    '''Modifies global mount_pt.'''
    global mount_pt
    try:
        TIMEOUT = 300
        INTERVAL = 3
        sleep_count = 0

        # Give the tester up to 5 minutes to reload the newly created CD/DVD
        print("Waiting up to 5 minutes for drive to be mounted ...")
        while True:
            time.sleep(INTERVAL)
            sleep_count = sleep_count + INTERVAL

            mount = run(
                f'mount "{optical_drive}" 2>&1 | grep -E -q "already mounted"',
                shell=True
            )
            if mount.returncode == 0:
                print("Drive appears to be mounted now")
                break

            # If they exceed the timeout limit, make a best effort to load the
            # tray in the next steps
            if sleep_count >= TIMEOUT:
                print("WARNING: TIMEOUT Exceeded and no mount detected!")
                break

        print("Deleting original data files ...")
        shutil.rmtree(SAMPLE_FILE)
        optical_drive_is_mounted = (
            run(
                f'mount | grep -q "{optical_drive}"',
                shell=True
            ).returncode == 0
        )
        if optical_drive_is_mounted:
            mount_pt = run(
                # TODO string notation
                f"mount | grep \"{optical_drive}\" | " + "awk '{print $3}'",
                shell=True,
                capture_output=True
            ).stdout
            print(f"Disk is mounted to {mount_pt}")
        else:
            print(f"Attempting best effort to mount {optical_drive} on my own")
            mount_pt = os.path.join(TEMP_DIR, 'mnt')
            print(f"Creating temp mount point: {mount_pt} ...")
            os.mkdir(mount_pt)

            print("Mounting disk to mount point ...")
            mount_subprocess = run(
                ['mount', optical_drive, mount_pt]
            )
            if mount_subprocess.returncode != 0:
                error = f"ERROR: Unable to re-mount {optical_drive}!"
                print(error, file=sys.stderr)
                raise RuntimeError(error)
        print("Copying files from ISO ...")
        run('cp $MOUNT_PT/* $TEMP_DIR', shell=True)
        run(
            ['check_md5', MD5SUM_FILE],
            check=True
        )
    except Exception as e:
        raise RuntimeError('Failed to verify files on optical disk') from e


def cleanup(optical_drive):
    print("Moving back to original location")
    os.chdir(START_DIR)
    print(f"Now residing in {os.getcwd()}")

    print("Cleaning up ...")
    if mount_pt:
        run(['unmount', mount_pt])
    shutil.rmtree(TEMP_DIR)

    print("Ejecting spent media ...")
    run(['eject', optical_drive])


def main():
    optical_drive = '/dev/sr0'
    optical_type = 'cd'
    try:
        device_path = sys.argv[1]
        # `[:-1]` removes the trailing b'\n' from the byte string.
        optical_drive = run(
              ['readlink', '-f', device_path],
              capture_output=True
          ).stdout[:-1]
    except IndexError:
        pass

    try:
        optical_type = sys.argv[2]
    except IndexError:
        pass

    exit_code = 0
    try:
        create_working_dirs()
        get_sample_data()
        generate_md5()
        generate_iso()
        burn_iso(optical_drive, optical_type)
        check_disk(optical_drive)
    except RuntimeError as e:
        print(e)
        print("Attempting to clean up ...")
        exit_code = 1
    finally:
        # always attempt cleanup (even on success)
        try:
            cleanup(optical_drive)
        except RuntimeError:
            print("Failed to clean up")
            exit_code = 1
        finally:
            sys.exit(exit_code)


if __name__ == "__main__":
    main()
