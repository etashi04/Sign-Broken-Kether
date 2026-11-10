"""Sign Korean patch installer. Uses the purchaser's bundled Ren'Py Python.
Only translation payloads, OFL font and reversible image/video differences ship.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, io, json, os, pickle, shutil, struct, sys, tempfile, uuid, zlib
sys.dont_write_bytecode = True

def digest(data): return hashlib.sha256(data).hexdigest()
def file_hash(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def contained(root, rel):
    p=PurePosixPath(rel)
    if p.is_absolute() or '..' in p.parts or '\\' in rel or ':' in rel: raise ValueError('Unsafe path: '+rel)
    dest=(root/rel).resolve()
    if not dest.is_relative_to(root.resolve()): raise ValueError('Path escaped target')
    return dest
class SafeIndex(pickle.Unpickler):
    def find_class(self,module,name): raise ValueError('Executable archive index rejected')
def archive_index(path):
    with path.open('rb') as f:
        head=f.read(40)
        if not head.startswith(b'RPA-3.0 '):raise ValueError('Unsupported archive')
        offset=int(head[8:24],16);key=int(head[25:33],16);f.seek(offset)
        index=SafeIndex(io.BytesIO(zlib.decompress(f.read()))).load()
    return {name:[(p[0]^key,p[1]^key,p[2] if len(p)>2 else b'') for p in parts] for name,parts in index.items()}
def member(path,parts):
    chunks=[]
    with path.open('rb') as f:
        for offset,length,prefix in parts:
            f.seek(offset);body=f.read(length)
            if len(body)!=length:raise EOFError('Truncated archive member')
            chunks.append(prefix+body)
    return b''.join(chunks)
def init_image_api(game):
    sys.path.insert(0,str(game))
    import renpy.pygame as pg
    return pg
def canonical_png(pg,data,scratch,name):
    # Compression zero produces a deterministic, directly comparable byte grid.
    src=scratch/(name+'_in');dst=scratch/(name+'_out.png');src.write_bytes(data)
    surface=pg.image.load(str(src));pg.image.save(surface,str(dst),0)
    result=dst.read_bytes();src.unlink();dst.unlink();return result
def xor_bytes(a,b,length):
    return (int.from_bytes(a,'little')^int.from_bytes(b,'little')).to_bytes(length,'little')
def compact_png(data):
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    pos=8;chunks=[];idat=[]
    while pos<len(data):
        size=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];body=data[pos+8:pos+8+size];pos+=12+size
        if kind==b'IDAT':idat.append(body)
        elif kind!=b'IEND':chunks.append((kind,body))
    chunks += [(b'IDAT',zlib.compress(zlib.decompress(b''.join(idat)),9)),(b'IEND',b'')]
    return data[:8]+b''.join(struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)) for k,b in chunks)
def load_package(package):
    manifest=json.loads((package/'manifest.json').read_text('utf-8'))
    for item in manifest['files']:
        src=contained(package,item['payload'])
        if file_hash(src)!=item['payload_sha256']:raise ValueError('Damaged payload: '+item['payload'])
    return manifest
def preflight(game,manifest):
    archive=game/'game/archive.rpa'
    if not archive.is_file() or not (game/'SignI.exe').is_file():raise ValueError('Select the folder containing SignI.exe')
    print('Checking original build / archive...',flush=True)
    if file_hash(archive)!=manifest['archive_sha256']:raise ValueError('Unsupported or modified build. No changes made.')
    return archive
def restore(game,state,backup):
    for row in reversed(state['files']):
        dst=contained(game/'game',row['path'])
        if row['existed']:
            src=contained(backup/'files',row['path']);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        elif dst.exists():dst.unlink()
def backup_root(game):
    root=game/'Sign_KO_Backup'
    legacy=game/'ETASHI_KO_BACKUP'
    if legacy.exists():
        if root.exists():raise ValueError('Legacy backup conflict; preserve both backup folders.')
        # Compatibility migration, within the selected game only. No deletion or overwrite.
        legacy.rename(root)
    return root
def install(game,package):
    manifest=load_package(package);archive=preflight(game,manifest)
    root=backup_root(game)
    statepath=root/'active.json'
    if statepath.exists():raise ValueError('Patch already installed. Remove it with this installer before reinstalling.')
    backup_name=manifest['version']
    backup=contained(root,backup_name)
    # A removed/abandoned backup is history, not an active installation.
    # Never replace or delete it: allocate a fresh backup for this attempt.
    while backup.exists():
        backup_name=manifest['version']+'_'+uuid.uuid4().hex[:12]
        backup=contained(root,backup_name)
    pg=init_image_api(game);index=archive_index(archive);outputs={}
    with tempfile.TemporaryDirectory(prefix='sign_ko_') as temp:
        scratch=Path(temp)
        for i,item in enumerate(manifest['files'],1):
            raw=contained(package,item['payload']).read_bytes()
            if item['kind']=='image_delta':
                base=member(archive,index[item['base_member']])
                if digest(base)!=item['base_sha256']:raise ValueError('Base asset mismatch: '+item['base_member'])
                canonical=canonical_png(pg,base,scratch,str(i))
                if digest(canonical)!=item['base_canonical_sha256']:raise ValueError('Image decoder mismatch; no files installed.')
                delta=zlib.decompress(raw)
                restored=xor_bytes(canonical,delta,len(delta))[:item['target_canonical_size']]
                if digest(restored)!=item['target_canonical_sha256']:raise ValueError('Image delta failed')
                raw=compact_png(restored)
            elif item['kind']=='video_delta':
                base=member(archive,index[item['base_member']])
                if digest(base)!=item['base_sha256']:raise ValueError('Base video mismatch: '+item['base_member'])
                delta=zlib.decompress(raw)
                if len(delta)!=item['target_size']:raise ValueError('Invalid video delta length')
                raw=xor_bytes(base[:len(delta)],delta,len(delta))
            if digest(raw)!=item['output_sha256']:raise ValueError('Output mismatch: '+item['path'])
            outputs[item['path']]=raw
            print('Prepared',i,'/',len(manifest['files']),item['path'],flush=True)
        # All outputs are verified before the first game-directory mutation.
        managed=set(outputs)
        for rel in tuple(managed):
            if rel.endswith('.rpy'):managed.add(rel[:-4]+'.rpyc')
        state={'version':manifest['version'],'backup_dir':backup_name,'files':[],'status':'preparing'}
        for rel in sorted(managed):
            dst=contained(game/'game',rel)
            row={'path':rel,'existed':dst.exists(),'before_sha256':file_hash(dst) if dst.exists() else None,
                 'installed_sha256':digest(outputs[rel]) if rel in outputs else None}
            if dst.exists():
                saved=contained(backup/'files',rel);saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,saved)
            state['files'].append(row)
        backup.mkdir(parents=True,exist_ok=True);statepath.parent.mkdir(parents=True,exist_ok=True)
        statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        try:
            for rel,raw in outputs.items():
                dst=contained(game/'game',rel);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
            # A pre-existing compiled file must not shadow the updated source.
            for rel in managed-set(outputs):
                dst=contained(game/'game',rel)
                if dst.exists():dst.unlink()
            for rel,raw in outputs.items():assert file_hash(contained(game/'game',rel))==digest(raw)
            state['status']='installed';statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        except BaseException:
            restore(game,state,backup);state['status']='rolled_back';statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');raise
    print('INSTALL PASS. Launch the game normally through Steam. Saves were not changed.',flush=True)
def uninstall(game):
    root=backup_root(game)
    statepath=root/'active.json'
    if not statepath.exists():raise ValueError('No active patch installation record')
    state=json.loads(statepath.read_text('utf-8'))
    backup=contained(root,state.get('backup_dir',state['version']))
    conflicts=[]
    for row in state['files']:
        dst=contained(game/'game',row['path'])
        # Compiled companions are engine-generated; every original is backed up.
        if row['installed_sha256'] and dst.exists() and file_hash(dst)!=row['installed_sha256']:conflicts.append(row['path'])
        if row['existed'] and file_hash(contained(backup/'files',row['path']))!=row['before_sha256']:raise ValueError('Backup damaged')
    if conflicts:raise ValueError('Files changed after installation; preserve and resolve them first: '+repr(conflicts))
    restore(game,state,backup)
    for row in state['files']:
        dst=contained(game/'game',row['path'])
        assert (file_hash(dst)==row['before_sha256']) if row['existed'] else not dst.exists()
    state['status']='removed';(backup/'removed.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');statepath.unlink()
    print('UNINSTALL PASS. Original loose files restored; archive and saves untouched.',flush=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['install','uninstall','verify']);parser.add_argument('game');args=parser.parse_args()
    game=Path(args.game).resolve();package=Path(__file__).resolve().parents[1]
    if args.action=='install':install(game,package)
    elif args.action=='uninstall':uninstall(game)
    else:preflight(game,load_package(package));print('VERIFY PASS')
if __name__=='__main__':
    try:main()
    except Exception as exc:print('FAILED:',exc,file=sys.stderr);sys.exit(1)
