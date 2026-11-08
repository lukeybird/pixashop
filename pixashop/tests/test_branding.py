"""Run after prepare.py: check product identity across the built UI source."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

class BrandingTests(unittest.TestCase):
    def test_prepared_product_has_no_upstream_promotional_labels(self):
        if not (ROOT / 'pixashop/.prepared').exists():
            self.skipTest('Run pixashop/prepare.py first')
        for directory in ['crates/ui-egui/src', 'apps/photocraft/src']:
            for file in (ROOT / directory).rglob('*.rs'):
                if 'credits' in file.parts or 'tests' in file.name:
                    continue
                text = file.read_text()
                for label in ['PhotoCraft', 'ArtCraft Website', 'Join the ArtCraft Discord', 'discord.gg/artcraft', 'getartcraft.com']:
                    self.assertNotIn(label, text, str(file.relative_to(ROOT)))

    def test_community_and_repository_menu_items_are_absent(self):
        text = (ROOT / 'crates/engine/src/shell_commands.rs').read_text()
        for command in ['help.discord', 'help.github', 'help.artcraftWebsite', 'help.reportIssue']:
            self.assertNotIn('"' + command + '"', text)

    def test_credits_and_licenses_remain_bundled(self):
        for name in ['LICENSE-MIT', 'LICENSE-APACHE', 'NOTICE', 'ATTRIBUTION.md', 'contributors/contributors.json']:
            self.assertTrue((ROOT / name).is_file(), name)
        self.assertIn("'NOTICE'", (ROOT / 'pixashop/package.py').read_text())

if __name__ == '__main__':
    unittest.main()
