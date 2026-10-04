"""Regression test: collect_artifacts with the `ignore` config on beets >= 2.13.

Beets 2.13 stopped converting the `ignore` patterns of `sorted_walk` to bytes.
The plugin walks a bytes path, so str patterns raised
`TypeError: cannot use a string pattern on a bytes-like object`.

This test does not use tests/helper.py, which needs an older beets test API.
Run: python -m pytest tests/test_ignore_patterns.py
"""
import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace

from beets import config

from beetsplug.copyartifacts import CopyArtifactsPlugin


class IgnorePatternTest(unittest.TestCase):
    def setUp(self):
        config.clear()
        config.read(user=False, defaults=True)
        config['ignore'] = ['.*', '*~', 'System Volume Information']
        self.src = tempfile.mkdtemp()
        self.dest = tempfile.mkdtemp()
        for name in ('01. track.flac', 'cover.jpg', 'origin.yaml', '.hidden', 'notes.txt~'):
            open(os.path.join(self.src, name), 'w').close()

    def tearDown(self):
        shutil.rmtree(self.src)
        shutil.rmtree(self.dest)

    def test_bytes_path_with_str_ignore_patterns(self):
        plugin = CopyArtifactsPlugin()
        item = SimpleNamespace(artist='7co', albumartist='7co', album='Neko Jarashi')
        source = os.path.join(self.src, '01. track.flac').encode()
        destination = os.path.join(self.dest, '01 - track.flac').encode()

        plugin.collect_artifacts(item, source, destination)

        queued = sorted(os.path.basename(f) for f in plugin._process_queue[0]['files'])
        self.assertEqual(queued, [b'cover.jpg', b'origin.yaml'])


if __name__ == '__main__':
    unittest.main()
