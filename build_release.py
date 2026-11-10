"""Build release packages on Windows with Python 3.12+ and .NET Framework C#.
No installed game or user-specific path is needed for packaging.
"""
from pathlib import Path
import ast,hashlib,json,os,shutil,subprocess,zipfile

ROOT=Path(__file__).resolve().parent
VERSION=(ROOT/'VERSION').read_text('utf8').strip()
PATCH=ROOT/'distribution/patch'
BUILD=ROOT/'build'/VERSION
DIST=ROOT/'dist'/VERSION

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def zip_folder(folder,destination):
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file():z.write(p,folder.name+'/'+p.relative_to(folder).as_posix())
    with zipfile.ZipFile(destination) as z:assert z.testzip() is None

def main():
    BUILD.mkdir(parents=True,exist_ok=True);DIST.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((PATCH/'manifest.json').read_text('utf8'))
    assert manifest['version']==VERSION
    for row in manifest['files']:assert sha(PATCH/row['payload'])==row['payload_sha256']
    payload=BUILD/'payload.zip'
    with zipfile.ZipFile(payload,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.write(PATCH/'manifest.json','manifest.json')
        z.write(ROOT/'src/install_backend.py','tools/install.py')
        for rel in sorted({r['payload'] for r in manifest['files']}):z.write(PATCH/rel,rel)
    auto=BUILD/'Sign Broken Kether 한국어 패치 (자동)';auto.mkdir(exist_ok=True)
    exe=auto/('Sign Broken Kether 한국어 패치 '+VERSION+'.exe')
    code=(ROOT/'src/SignBrokenKether_Installer.cs').read_text('utf-8-sig')
    assert 'const string Version = "'+VERSION+'"' in code
    generated=BUILD/'Installer.cs';generated.write_text(code.replace('__PAYLOAD_SHA256__',sha(payload).upper()),'utf-8-sig')
    csc=Path(os.environ.get('WINDIR','C:/Windows'))/'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    subprocess.run([str(csc),'/nologo','/target:winexe','/platform:x64','/optimize+',
        '/reference:System.Windows.Forms.dll','/reference:System.Drawing.dll',
        '/reference:System.IO.Compression.dll','/reference:System.IO.Compression.FileSystem.dll',
        '/win32icon:'+str(ROOT/'assets/installer.ico'),
        '/resource:'+str(ROOT/'assets/installer.ico')+',InstallerIcon',
        '/resource:'+str(ROOT/'assets/capsule.png')+',InstallerLogo',
        '/resource:'+str(payload)+',payload.zip','/out:'+str(exe),str(generated)],check=True)
    shutil.copy2(ROOT/'distribution/docs/auto_readme.txt',auto/'README.txt')
    shutil.copy2(ROOT/'THIRD_PARTY_NOTICES.txt',auto/'제3자_라이선스_고지.txt')
    manual=BUILD/'Sign Broken Kether 한국어 패치 (수동)';game=manual/'패치파일/game'
    game.mkdir(parents=True,exist_ok=True)
    resources=game/'ko_patch_resources';resources.mkdir(exist_ok=True)
    for row in manifest['files']:
        dst=(game/row['path']) if row['kind']=='file' else (resources/row['payload'])
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PATCH/row['payload'],dst)
    dm={k:manifest[k] for k in ['archive_sha256','archive_size','supported_build','steam_appid']}
    dm.update(version=VERSION,exe_sha256='f0e95e331d0488c9057dfd1ff720df1d720438176af10290ff0f5b0bc807289b',
        files=[r for r in manifest['files'] if r['kind']!='file'])
    (resources/'manifest.json').write_text(json.dumps(dm,ensure_ascii=False,indent=2)+'\n','utf8')
    shared=(ROOT/'src/install_backend.py').read_text('utf8');tree=ast.parse(shared)
    names={'digest','file_hash','contained','SafeIndex','archive_index','member','canonical_png','xor_bytes','compact_png'}
    decoder='from pathlib import Path, PurePosixPath\nimport hashlib,io,pickle,struct,zlib\n'
    decoder+='\n\n'.join(ast.get_source_segment(shared,n) for n in tree.body if getattr(n,'name',None) in names)+'\n'
    (resources/'decoder.py').write_text(decoder,'utf8')
    shutil.copy2(ROOT/'src/manual_runtime.py',resources/'runtime.py')
    shutil.copy2(ROOT/'src/manual_bootstrap.rpy',game/'zz_ko_manual_resources.rpy')
    shutil.copy2(ROOT/'distribution/docs/manual_readme.txt',manual/'README.txt')
    shutil.copy2(ROOT/'THIRD_PARTY_NOTICES.txt',manual/'제3자_라이선스_고지.txt')
    outputs=[]
    for folder,name in [(auto,'Sign_Broken_Kether_Korean_Patch_'+VERSION+'.zip'),
                        (manual,'Sign_Broken_Kether_Korean_Patch_Manual_'+VERSION+'.zip')]:
        target=DIST/name;zip_folder(folder,target);outputs.append(target)
    (DIST/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in outputs),'utf8')
    print('Built Auto, Manual, SHA256SUMS.txt. Installation/runtime QA is a separate step.')

if __name__=='__main__':main()
