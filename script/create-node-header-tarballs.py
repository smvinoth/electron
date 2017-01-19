#!/usr/bin/env python

import argparse
import os
import shutil
import sys
import tarfile

from lib.util import safe_mkdir, scoped_cwd, rm_rf


SOURCE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DIST_DIR    = os.path.join(SOURCE_ROOT, 'dist')
NODE_DIR    = os.path.join(SOURCE_ROOT, 'vendor', 'node')

HEADERS_SUFFIX = [
  '.h',
  '.gypi',
]
HEADERS_DIRS = [
  'src',
  'deps/http_parser',
  'deps/zlib',
  'deps/uv',
  'deps/npm',
  'deps/mdb_v8',
]
HEADERS_FILES = [
  'common.gypi',
  'config.gypi',
]


def main():
  args = parse_args()

  safe_mkdir(DIST_DIR)

  node_headers_dir = os.path.join(DIST_DIR, 'node-headers')
  rm_rf(node_headers_dir)
  copy_headers(node_headers_dir)

  version = args.version
  create_header_tarball(node_headers_dir, 'node-{0}'.format(version))
  create_header_tarball(node_headers_dir, 'iojs-{0}'.format(version))
  create_header_tarball(node_headers_dir, 'iojs-{0}-headers'.format(version))


def parse_args():
  parser = argparse.ArgumentParser(description='Create Node header tarballs')
  parser.add_argument('-v', '--version', help='Specify the version',
                      required=True)
  return parser.parse_args()


def copy_headers(dist_headers_dir):
  safe_mkdir(dist_headers_dir)

  # Copy standard node headers from the Node repo.
  for include_path in HEADERS_DIRS:
    abs_path = os.path.join(NODE_DIR, include_path)
    for dirpath, _, filenames in os.walk(abs_path):
      for filename in filenames:
        extension = os.path.splitext(filename)[1]
        if extension not in HEADERS_SUFFIX:
          continue
        copy_source_file(os.path.join(dirpath, filename), NODE_DIR,
                         dist_headers_dir)
  for other_file in HEADERS_FILES:
    copy_source_file(os.path.join(NODE_DIR, other_file), NODE_DIR,
                     dist_headers_dir)

  # Copy V8 headers from the Chromium repo.
  src = os.path.join(SOURCE_ROOT, 'vendor', 'brightray', 'vendor', 'download',
                    'libchromiumcontent', 'src')
  for dirpath, _, filenames in os.walk(os.path.join(src, 'v8')):
    for filename in filenames:
      extension = os.path.splitext(filename)[1]
      if extension not in HEADERS_SUFFIX:
        continue
      copy_source_file(os.path.join(dirpath, filename), src,
                       os.path.join(dist_headers_dir, 'deps'))


def create_header_tarball(dist_headers_dir, tarball_name):
  target = os.path.join(DIST_DIR, tarball_name) + '.tar.gz'
  with scoped_cwd(DIST_DIR):
    tarball = tarfile.open(name=target, mode='w:gz')
    tarball.add(os.path.relpath(dist_headers_dir), arcname=tarball_name)
    tarball.close()


def copy_source_file(source, start, destination):
  relative = os.path.relpath(source, start=start)
  final_destination = os.path.join(destination, relative)
  safe_mkdir(os.path.dirname(final_destination))
  shutil.copy2(source, final_destination)


if __name__ == '__main__':
  sys.exit(main())
