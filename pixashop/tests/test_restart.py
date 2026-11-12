"""Exercise replacement and rollback using a fake Applications directory."""
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'overlay/crates/ui-egui/src/pixashop_restart.sh'

class RestartTests(unittest.TestCase):
    def scenario(self, bad_signature=False, fail_launch=False):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'stage'
            root.mkdir()
            target = base / 'PixaShop.app'
            target.mkdir()
            (target / 'version').write_text('old')
            (root / 'PixaShop.app').mkdir()
            (root / 'PixaShop.app/version').write_text('new')
            sign = base / 'codesign'
            sign.write_text('#!/bin/sh\n' + ('exit 1\n' if bad_signature else 'echo TeamIdentifier=945M5X4DY3 >&2\necho Identifier=com.aiwebdesignfirm.pixashop >&2\n'))
            sign.chmod(0o700)
            launch = base / 'open'
            launch.write_text('#!/bin/sh\n' + ('test "$(cat "$1/version")" = old\n' if fail_launch else 'exit 0\n'))
            launch.chmod(0o700)
            script = SCRIPT.read_text().replace('/usr/bin/codesign', str(sign)).replace('/usr/sbin/spctl', '/usr/bin/true').replace('/usr/bin/open', str(launch))
            file = base / 'restart.sh'
            file.write_text(script)
            # Use a process that has already exited so the real wait loop falls through.
            exited = subprocess.Popen(['/usr/bin/true'])
            exited.wait()
            result = subprocess.run(['/bin/sh', str(file), str(exited.pid), str(root), str(target)], capture_output=True)
            return result.returncode, (target / 'version').read_text(), root.exists()

    def test_verified_update_replaces_app_and_cleans_staging(self):
        self.assertEqual(self.scenario(), (0, 'new', False))

    def test_failed_signature_preserves_original(self):
        code, version, _ = self.scenario(bad_signature=True)
        self.assertNotEqual(code, 0)
        self.assertEqual(version, 'old')

    def test_failed_launch_restores_original(self):
        code, version, _ = self.scenario(fail_launch=True)
        self.assertNotEqual(code, 0)
        self.assertEqual(version, 'old')

if __name__ == '__main__':
    unittest.main()
