"""Product-facing branding cleanup; preserve source provenance and legal credits."""
from pathlib import Path
import re

PRODUCT_URL = 'https://aiwebdesignfirm.com/pixashop'


def clean_catalog(text):
    """Retire unused upstream promotional keys, never rewrite contributor identities."""
    lines = []
    for line in text.splitlines(keepends=True):
        fields = line.rstrip('\r\n').split('\t')
        key = fields[1] if len(fields) >= 3 else ''
        if key == 'ArtCraft' or 'ArtCraft Website' in key or 'Join the ArtCraft Discord' in key:
            continue
        lines.append(line)
    return ''.join(lines)


def clean_packaging(text, name):
    text = text.replace('https://getartcraft.com/apps/photocraft', PRODUCT_URL)
    text = text.replace('https://github.com/storytold/photocraft/issues', PRODUCT_URL)
    text = text.replace('https://github.com/storytold/photocraft</url>', PRODUCT_URL + '/manual</url>')
    text = text.replace('https://discord.gg/artcraft', PRODUCT_URL)
    text = text.replace('vendor: Learning Machines LLC', 'vendor: AIWebDesignFirm')
    text = text.replace('<developer id="ai.storyteller">', '<developer id="com.aiwebdesignfirm">')
    if '.metainfo.xml' in name:
        # An upstream screenshot does not depict the Pixa edition; do not advertise it.
        text = re.sub(r'  <screenshots>[\s\S]*?</screenshots>\n', '', text)
    return text


def finish_branding(root: Path):
    for file in (root / 'crates/ui-egui/src/i18n').glob('*.tsv'):
        file.write_text(clean_catalog(file.read_text(encoding='utf-8')), encoding='utf-8')
    for file in (root / 'packaging').rglob('*'):
        if file.is_file() and file.suffix in {'.in', '.yaml', '.yml', '.xml'}:
            file.write_text(clean_packaging(file.read_text(encoding='utf-8'), file.name), encoding='utf-8')
