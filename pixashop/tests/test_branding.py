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

class ComprehensiveBrandingTests(unittest.TestCase):
    def test_translated_promotional_keys_are_retired(self):
        import sys
        sys.path.insert(0, str(ROOT / 'pixashop'))
        from branding import clean_catalog
        before = '\tArtCraft Website\tSite ArtCraft\n\tArtCraft\tArtCraft\n\tJoin the ArtCraft Discord…\tDiscord\n\tContributors\tContributors\n# Copyright ArtCraft contributors\n'
        self.assertEqual(clean_catalog(before), '\tContributors\tContributors\n# Copyright ArtCraft contributors\n')
        if not (ROOT / 'pixashop/.prepared').exists():
            self.skipTest('Run preparation to audit generated catalogs')
        for file in (ROOT / 'crates/ui-egui/src/i18n').glob('*.tsv'):
            for line in file.read_text().splitlines():
                fields = line.split('\t')
                key = fields[1] if len(fields) >= 3 else ''
                self.assertFalse(key == 'ArtCraft' or 'ArtCraft Website' in key or 'Join the ArtCraft Discord' in key, str(file))

    def test_packaging_promotional_metadata_is_ours(self):
        import sys
        sys.path.insert(0, str(ROOT / 'pixashop'))
        from branding import clean_packaging
        fixture = '<screenshots><image>upstream</image></screenshots>\n  <screenshots>old</screenshots>\n<url>https://discord.gg/artcraft</url>\nvendor: Learning Machines LLC\n'
        cleaned = clean_packaging(fixture, 'product.metainfo.xml.in')
        self.assertNotIn('  <screenshots>', cleaned)
        self.assertNotIn('discord.gg', cleaned)
        self.assertIn('vendor: AIWebDesignFirm', cleaned)
        if not (ROOT / 'pixashop/.prepared').exists():
            self.skipTest('Run preparation to audit generated metadata')
        for relative in ['packaging/linux/nfpm.yaml', 'packaging/linux/com.aiwebdesignfirm.pixashop.metainfo.xml.in']:
            text = (ROOT / relative).read_text()
            for forbidden in ['getartcraft.com', 'discord.gg/artcraft', 'Learning Machines LLC', 'https://github.com/storytold/photocraft', '<screenshots>']:
                self.assertNotIn(forbidden, text, relative)

    def test_own_manual_update_channel_and_icon(self):
        self.assertIn("render('S',", (ROOT / 'pixashop/icons.py').read_text())
        for path in ['pixashop/manual/guide.json', 'pixashop/manual/tools.json']:
            text = (ROOT / path).read_text()
            for forbidden in ['getartcraft.com', 'discord.gg/artcraft', 'https://github.com/storytold/photocraft']:
                self.assertNotIn(forbidden, text)
        for file in (ROOT / 'pixashop/overlay').rglob('*.rs'):
            self.assertNotIn('api.github.com/repos/storytold/', file.read_text())
        self.assertIn("'.build.json'", (ROOT / 'pixashop/package.py').read_text())
