#!/usr/bin/env python3
"""Apply the PixaShop product overlay to a clean, pinned PhotoCraft checkout.

Keep internal crate identifiers and .pcraft compatibility. No upstream update binaries,
branding services, or signing identities are used in the finished product.
"""
from pathlib import Path
import shutil
import sys
import re

ROOT = Path(__file__).resolve().parent.parent

def patch(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f'Upstream changed the integration point: {path}')
    p.write_text(text.replace(old, new), encoding='utf-8')

def prepare():
    patch('Cargo.toml', 'version = "0.20.1"', 'version = "0.20.3"')
    # Display strings and translated catalogs; preserve contributor credits and legal notices.
    for parent in ['apps', 'crates', 'packaging']:
        for p in (ROOT / parent).rglob('*'):
            if p.is_file() and p.suffix in {'.rs', '.tsv', '.html', '.in', '.xml', '.desktop', '.wxs', '.wxl', '.ps1', '.sh', '.txt'}:
                if p.suffix != '.rs' and any(x in p.name.lower() for x in ['license', 'attribution', 'notice']):
                    continue
                try:
                    text = p.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    continue
                # Keep authorship/copyright truthful while changing product-facing text.
                text = '\n'.join(line if 'copyright' in line.lower() else line.replace('PhotoCraft', 'PixaShop').replace('"Photocraft"', '"PixaShop"') for line in text.split('\n'))
                text = text.replace('ai.storyteller.photocraft', 'com.aiwebdesignfirm.pixashop')
                text = text.replace('Learning Machines LLC', 'AIWebDesignFirm')
                p.write_text(text, encoding='utf-8')
    for p in (ROOT / 'pixashop/overlay').rglob('*'):
        if p.is_file():
            target = ROOT / p.relative_to(ROOT / 'pixashop/overlay')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, target)
    patch('crates/ui-egui/src/lib.rs', 'mod updates_ui;', 'mod updates_ui;\nmod pixashop_updater;')
    patch('apps/photocraft/src/main.rs', 'mod updates;', 'mod updates;\nmod access;')
    patch('apps/photocraft/src/main.rs', 'Ok(Box::new(app))', 'Ok(Box::new(access::AccessApp::new(app)))')
    # Upstream's restart helper has a different bundle identity. Updates are offered as our
    # own OS installer downloads until a separately signed PixaShop updater is released.
    p = ROOT / 'apps/photocraft/src/main.rs'
    text = p.read_text(encoding='utf-8')
    text = re.sub(r'    #\[cfg\(not\(target_arch = "wasm32"\)\)\]\n    if let Some\(done\) = craft_update::self_update::finish\([\s\S]*?\n    }\n', '', text, count=1)
    p.write_text(text, encoding='utf-8')
    # Own update metadata and no inherited developer or release identities.
    p = ROOT / 'crates/ui-egui/src/lib.rs'
    text = p.read_text(encoding='utf-8').replace('..craft_update::suite::PHOTOCRAFT', 'developer: "AIWebDesignFirm",\n    ..craft_update::app::App::new("pixashop", "PixaShop", "Image editing", "lukeybird/pixashop")')
    p.write_text(text, encoding='utf-8')
    for rel in ['crates/engine/src/cmd/updates_cmds.rs', 'crates/ui-egui/src/updates_ui.rs']:
        p = ROOT / rel
        p.write_text(p.read_text(encoding='utf-8').replace('https://github.com/storytold/photocraft/releases', 'https://github.com/lukeybird/pixashop/releases'), encoding='utf-8')
    p = ROOT / 'crates/ui-egui/src/links.rs'
    text = p.read_text(encoding='utf-8').replace('https://discord.gg/artcraft', 'https://aiwebdesignfirm.com/account')
    text = text.replace('https://getartcraft.com/apps/photocraft', 'https://aiwebdesignfirm.com/pixashop')
    text = text.replace('https://getartcraft.com/tutorials', 'https://aiwebdesignfirm.com/pixashop')
    text = text.replace('https://getartcraft.com', 'https://aiwebdesignfirm.com')
    text = text.replace('https://github.com/storytold/photocraft', 'https://github.com/lukeybird/pixashop')
    text = text.replace('Join us on Discord', 'Manage your account').replace('tl!("ArtCraft")', '"AIWebDesignFirm"')
    p.write_text(text, encoding='utf-8')
    # Do not send customers to the upstream community or display its promotional brand marks.
    for p in (ROOT / 'crates/ui-egui/src').rglob('*.rs'):
        if 'credits' in p.parts:
            continue
        text = p.read_text(encoding='utf-8').replace('Join the ArtCraft Discord', 'Manage your AIWebDesignFirm account').replace('ArtCraft Website', 'AIWebDesignFirm Website')
        p.write_text(text, encoding='utf-8')
    patch('apps/photocraft/Cargo.toml', 'craft-update = { workspace = true }', 'craft-update = { workspace = true }\nureq = { version = "3.4", features = ["json"] }')
    # Keep preferences/recovery separate from an existing upstream installation.
    p = ROOT / 'apps/photocraft/src/app_dirs.rs'
    p.write_text(p.read_text(encoding='utf-8').replace('"photocraft"', '"pixashop"').replace('PHOTOCRAFT_CONFIG_DIR', 'PIXASHOP_CONFIG_DIR'), encoding='utf-8')
    # About describes this product; upstream authorship stays in Contributors and licenses.
    p = ROOT / 'crates/ui-egui/src/dialogs.rs'
    text = p.read_text(encoding='utf-8').replace('PixaShop — an open-source, native image editor written in Rust.', 'PixaShop by AIWebDesignFirm — your desktop image editor.')
    p.write_text(text, encoding='utf-8')
    # Bundle the guide and expose it without a network dependency or an open document.
    patch('crates/ui-egui/src/lib.rs', 'mod pixashop_updater;', 'mod pixashop_updater;\nmod pixashop_manual;')
    patch('crates/engine/src/shell_commands.rs',
          '    ("help.website", "PixaShop Website", &["Help"], None),',
          '    ("help.manual", "PixaShop User Manual…", &["Help"], None),\n    ("help.website", "PixaShop Website", &["Help"], None),')
    patch('crates/ui-egui/src/menus/state.rs',
          '        i if crate::links::url_for(i).is_some() => true,',
          '        "help.manual" => true,\n        i if crate::links::url_for(i).is_some() => true,')
    patch('crates/ui-egui/src/menus/invoke.rs',
          '    if let Some(url) = crate::links::url_for(id) {',
          '    if id == "help.manual" { crate::pixashop_manual::open(ctx); return Some(Ok(json!({"manual": true}))); }\n    if let Some(url) = crate::links::url_for(id) {')
    patch('crates/ui-egui/src/app/frame.rs',
          '        updates_ui::show(self, &ctx);',
          '        updates_ui::show(self, &ctx);\n        crate::pixashop_manual::show(self, &ctx);')
    p = ROOT / 'crates/ui-egui/src/links.rs'
    text = p.read_text(encoding='utf-8').replace('pub const TUTORIALS: &str = "https://aiwebdesignfirm.com/pixashop";', 'pub const TUTORIALS: &str = "https://aiwebdesignfirm.com/pixashop/manual";')
    text = text.replace('                "help.website",', '                "help.manual",\n                "help.website",')
    p.write_text(text, encoding='utf-8')
    # The commercial desktop does not expose an unauthenticated automation surface.
    patch('apps/photocraft/src/main.rs',
          '    let (port, warning) = control_port_for(cli_port, &integrations(services::prefs_file().as_deref()));',
          '    if !access::automation_enabled() { return None; }\n    let (port, warning) = control_port_for(cli_port, &integrations(services::prefs_file().as_deref()));')
    # include_str! fixtures and platform installers use the new application identifier.
    for source in (ROOT / 'packaging').rglob('*'):
        if source.is_file() and 'ai.storyteller.photocraft' in source.name:
            target = source.with_name(source.name.replace('ai.storyteller.photocraft', 'com.aiwebdesignfirm.pixashop'))
            shutil.copyfile(source, target)
    # mkfifoat is not exposed by rustix on macOS. Use the POSIX tool in this Unix-only test.
    patch('apps/photocraft/src/external_svg.rs',
          'rustix::fs::mkfifoat(rustix::fs::CWD, &owned.file, rustix::fs::Mode::RUSR | rustix::fs::Mode::WUSR).unwrap();',
          'assert!(std::process::Command::new("mkfifo").args(["-m", "600"]).arg(&owned.file).status().unwrap().success());')
    # Install custom vector-derived icon assets generated by pixashop/icons.py.
    from icons import generate
    generate(ROOT)
    (ROOT / 'pixashop/.prepared').write_text('PixaShop by AIWebDesignFirm\n')
    print('Prepared PixaShop by AIWebDesignFirm. Build the existing photocraft Cargo target.')

if __name__ == '__main__':
    try:
        prepare()
    except (OSError, RuntimeError) as error:
        print(f'PixaShop preparation failed: {error}', file=sys.stderr)
        sys.exit(1)
