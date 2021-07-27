#!/usr/bin/env python3

from arrow import Arrow
from pathlib import Path
from os import environ
from subprocess import run
from tempfile import mkdtemp
from shutil import rmtree

from pprint import pprint

class DCIM():
    def __init__(self, device=None, source=None, target=None, confirm=False, date_path=True):
        self.device=device or environ['DCIM_DEVICE']
        self.source=source or environ['DCIM_SOURCE'] 
        self.target = str(self.make_target_path(target or environ['DCIM_TARGET'], date_path))
        self.confirm=confirm

    def __enter__(self):
        self.temp_dir = Path(mkdtemp())
        return self

    def __exit__(self, etype, value, tb):
        rmtree(str(self.temp_dir))
        return False

    def output(self, argv):
        p = run(argv, capture_output=True, universal_newlines=True)
        lines = [l for l in p.stdout.split('\n') if l]
        return lines

    def call(self, args):
        return run(args)

    def rsync(self, args=[], target=True):
        argv = ['rsync']
        argv.extend(args)
        argv.append(self.device+':'+self.source)
        if target:
            argv.append(self.target)
        return argv

    def ssh(self, cmd='uname', source=True):
        if source:
            _cmd = f"cd {self.source};{cmd}"
        else:
            _cmd = cmd
        return ['ssh', self.device, _cmd]

    def get_source_files(self):
        source_files = self.output(self.rsync(['-az', '--list-only'], target=False))
        self.write_output_file(source_files, 'source_files')
        return source_files

    def copy_files(self):
        return self.call(self.rsync(['-az','--info=progress2']))

    def get_file_list(self):
        files = self.output(self.ssh('find . -type f'))
        self.list_file = self.write_output_file(files, 'file_list')
        return files

    def write_output_file(self, lines, filename):
        outpath = self.temp_dir / filename
        outpath.write_text('\n'.join(lines))
        return str(outpath)

    def get_source_checksums(self):
        file_list = self.get_file_list()
        checksums = []
        for pathname in file_list:
            checksums.append(self.get_md5_checksum(pathname))
        self.checksum_file = self.write_output_file(checksums, 'checksums')
        return checksums

    def get_md5_checksum(self, pathname):
        return self.output(self.ssh(f'md5sum {pathname}'))[0]

    def verify_target_checksums(self):
        ret=[]
        self.get_source_checksums()
        p = run(['md5sum', '-c', self.checksum_file], cwd=self.target, universal_newlines=True, capture_output=True)
        if p.returncode==0:
            for line in str(p.stdout).split('\n'):
                if not line:
                    continue
                if not line.endswith(': OK'):
                    raise RuntimeError(f'Target Checksum Verify failed: {line}')
                else:
                    ret.append(line[:-4])
            return ret
        else:
            print(p.stderr)
            return False

    def make_target_path(self, target, date_path):
        target = Path(target)
        if not target.exists():
            target.mkdir()
        if date_path:
            target = target / Arrow.now().date().strftime('%Y-%m-%d-DCIM')
            if not target.exists():
                target.mkdir()
        return target

    def delete_source(self, pathname):
        return self.call(self.ssh(f"rm {pathname}"))
