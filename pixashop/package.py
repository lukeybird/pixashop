#!/usr/bin/env python3
"""Package the compiled editor under PixaShop's identity; never relabel an upstream binary."""
from pathlib import Path
import os, platform, shutil, subprocess, sys, tarfile, tomllib, zipfile, hashlib, json
ROOT=Path(__file__).resolve().parent.parent

def package():
    version=tomllib.loads((ROOT/'Cargo.toml').read_text())['workspace']['package']['version']
    if not (ROOT/'pixashop/.prepared').exists():
        raise RuntimeError('Run pixashop/prepare.py before compiling the editor.')
    out=ROOT/'dist/pixashop'; out.mkdir(parents=True,exist_ok=True)
    system=platform.system()
    target=Path(os.environ.get('CARGO_TARGET_DIR',ROOT/'target'))
    stage=out/'stage'
    if stage.exists(): shutil.rmtree(stage)
    stage.mkdir()
    licenses=stage/'Licenses'; licenses.mkdir(exist_ok=True)
    for name in ['LICENSE-MIT','LICENSE-APACHE','NOTICE','ATTRIBUTION.md']:
        shutil.copyfile(ROOT/name,licenses/name)
    # Preserve all bundled font, dictionary and icon license notices.
    for source in (ROOT/'assets').rglob('*'):
        if source.is_file() and any(x in source.name.lower() for x in ['license','ofl-','attribution']):
            dest=licenses/source.relative_to(ROOT/'assets');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    if system=='Windows':
        shutil.copyfile(target/'release/photocraft.exe',stage/'PixaShop.exe')
        (stage/'portable.txt').write_text('PixaShop portable installation\n')
        asset=out/f'pixashop-{version}-windows-x64-portable.zip'
        with zipfile.ZipFile(asset,'w',zipfile.ZIP_DEFLATED) as archive:
            for p in stage.rglob('*'):
                if p.is_file():archive.write(p,Path('PixaShop')/p.relative_to(stage))
    elif system=='Darwin':
        app=stage/'PixaShop.app'; macos=app/'Contents/MacOS'; resources=app/'Contents/Resources';macos.mkdir(parents=True,exist_ok=True);resources.mkdir(parents=True,exist_ok=True)
        subprocess.run(['lipo','-create',str(target/'aarch64-apple-darwin/release/photocraft'),str(target/'x86_64-apple-darwin/release/photocraft'),'-output',str(macos/'pixashop')],check=True)
        shutil.copyfile(ROOT/'assets/app-icon/photocraft.icns',resources/'PixaShop.icns');shutil.copytree(licenses,resources/'Licenses',dirs_exist_ok=True)
        import plistlib
        with (app/'Contents/Info.plist').open('wb') as f:
            plistlib.dump({'CFBundleName':'PixaShop','CFBundleDisplayName':'PixaShop','CFBundleIdentifier':'com.aiwebdesignfirm.pixashop','CFBundleExecutable':'pixashop','CFBundlePackageType':'APPL','CFBundleShortVersionString':version,'CFBundleVersion':version,'CFBundleIconFile':'PixaShop','LSMinimumSystemVersion':'11.0','NSHighResolutionCapable':True},f)
        subprocess.run(['codesign','--force','--deep','--sign','-',str(app)],check=True)
        asset=out/f'pixashop-{version}-macos-universal.dmg'
        from macos_dmg import build_installer
        build_installer(app, asset)
    else:
        shutil.copyfile(target/'release/photocraft',stage/'pixashop');(stage/'pixashop').chmod(0o755)
        asset=out/f'pixashop-{version}-linux-x86_64.tar.gz'
        with tarfile.open(asset,'w:gz') as archive:archive.add(stage,arcname='PixaShop')
    digest=hashlib.sha256(asset.read_bytes()).hexdigest()
    (out/(asset.name+'.sha256')).write_text(f'{digest}  {asset.name}\n')
    # Bind the artifact to product source, not an unrelated upstream release tag.
    source_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    receipt={'product':'PixaShop','version':version,'source_commit':source_commit,'asset':asset.name,'sha256':digest,'signed':False,'status':'testing-only','branding_audit':'source checks; installed UI verification still required'}
    (out/(asset.name+'.build.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'asset':str(asset),'sha256':digest,'signed':False,'status':'testing-only'}))
    return asset

if __name__=='__main__':
    try:package()
    except (OSError,RuntimeError,subprocess.CalledProcessError) as error:
        print(f'PixaShop packaging failed: {error}',file=sys.stderr);sys.exit(1)
