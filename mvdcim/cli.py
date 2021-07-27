#!/usr/bin/env python3

import arrow
import click

from pathlib import Path

from mvdcim import DCIM, __version__, __license__

class ChecksumVerifyFailure(Exception):
    pass

class VerifiedFileListMismatch(Exception):
    pass

class SourceDeleteFailed(Exception):
    pass


@click.command(name='mvdkim')
@click.version_option(message=f"mvdkim v{__version__} {__license__}")
@click.option('-y', '--yes', is_flag=True, default=False, help='automate confirmation prompt')
@click.argument('device', envvar='DCIM_DEVICE', type=str, default='android')
@click.argument('source', envvar='DCIM_SOURCE', type=str, default='/sdcard/DCIM')
@click.argument('target', envvar='DCIM_TARGET', type=str, default='/archive/phone/camera')
def mvdcim(yes, device, source, target):
    with DCIM(device, source, target, confirm=yes) as dcim:
        file_list = dcim.get_file_list()
        dcim.copy_files()
        verified_files = dcim.verify_target_checksums()
        if not verified_files:
            raise ChecksumVerifyFailure
        if file_list != verified_files:
            raise VerifiedFileMismatch
        for filename in file_list:
            if not dcim.delete_source(filename):
                raise SourceDeleteFailed
