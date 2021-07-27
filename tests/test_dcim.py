# mvdcim tests

import mvdcim

import os
import pytest
from pprint import pprint as pp
from tempfile import NamedTemporaryFile
import subprocess
from pathlib import Path

@pytest.fixture(scope='module')
@pytest.mark.skipif(not os.environ.get('DCIM_DEVICE'), reason='define DCIM_DEVICE to enable')
@pytest.mark.skipif(not os.environ.get('DCIM_SOURCE'), reason='define DCIM_SOURCE to enable')
@pytest.mark.skipif(not os.environ.get('DCIM_TARGET'), reason='define DCIM_TARGET to enable')
def dcim():
    with mvdcim.DCIM() as dcim:
        yield dcim

def test_init(dcim):
    print()
    assert dcim
    assert isinstance(dcim, mvdcim.DCIM)

def test_get_source_files(dcim):
    files = dcim.get_source_files()
    assert isinstance(files, list)
    assert len(files)
    for file in files:
        print(file)

def test_get_file_list(dcim):
    print()
    files = dcim.get_file_list()
    assert isinstance(files, list)
    assert len(files)
    for file in files:
        print(file)

def test_copy_files(dcim):
    print()
    dcim.copy_files()

def test_md5_checksum_and_copy(dcim):
    print()
    dcim.copy_files()
    files = dcim.get_file_list()
    for line in files:
        md5sum = dcim.get_md5_checksum(line)
        assert len(md5sum)
        assert isinstance(md5sum, str)
        print(md5sum)

def test_checksums(dcim):
    print()
    file_list = dcim.get_file_list()
    dcim.copy_files()
    verified_files = dcim.verify_target_checksums()
    assert verified_files, 'target checksum verify failed!'
    assert len(verified_files)
    assert isinstance(verified_files, list)

    assert file_list == verified_files, "source/target verify failed"
    for filename in file_list:
        print(f'delete verified: {filename}')
