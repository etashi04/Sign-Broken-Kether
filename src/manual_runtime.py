"""First-run resource preparation for the copy-only Korean patch.

Uses only original assets from the purchaser's archive and verified deltas.
The original archive, saves and automatic-installer backup history are not written.
"""
from pathlib import Path
import importlib.util, json, os, tempfile

def prepare(game_root, pg):
    game=Path(game_root).resolve()
    package=Path(__file__).resolve().parent
    spec=importlib.util.spec_from_file_location('_sign_ko_delta_decoder',package/'decoder.py')
    decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
    data=(package/'manifest.json').read_bytes()
    manifest=json.loads(data)
    archive=game/'game/archive.rpa'
    if any((game/name/'active.json').exists() for name in ['Sign_KO_Backup','ETASHI_KO_BACKUP']):
        raise RuntimeError('자동 설치판이 적용되어 있습니다. 원본 복구 후 수동판을 설치해 주세요.')
    if not archive.is_file() or not (game/'SignI.exe').is_file():
        raise RuntimeError('Sign: Broken Kether 정품 게임 폴더에 수동 패치를 복사해 주세요.')
    stamp=package/'prepared.json'
    signature={'manifest':decoder.digest(data),'archive_size':archive.stat().st_size,
               'archive_mtime':archive.stat().st_mtime_ns}
    if stamp.is_file():
        try:
            previous=json.loads(stamp.read_text('utf8'))
            if previous['signature']==signature and all(
                (game/'game'/r['path']).is_file() and
                decoder.file_hash(game/'game'/r['path'])==r['output_sha256'] for r in manifest['files']):
                return False
        except (OSError,ValueError,KeyError):pass
    if decoder.file_hash(game/'SignI.exe')!=manifest['exe_sha256'] or decoder.file_hash(archive)!=manifest['archive_sha256']:
        raise RuntimeError('지원 게임 빌드와 원본이 다릅니다. Steam 빌드 26422637용 패치를 사용해 주세요.')
    index=decoder.archive_index(archive)
    outputs={}
    with tempfile.TemporaryDirectory(prefix='sign_ko_manual_') as work:
        scratch=Path(work)
        for i,row in enumerate(manifest['files']):
            raw=decoder.contained(package,row['payload']).read_bytes()
            if decoder.digest(raw)!=row['payload_sha256']:
                raise RuntimeError('수동 패치 데이터가 손상됐습니다. ZIP을 다시 받아 주세요.')
            base=decoder.member(archive,index[row['base_member']])
            if decoder.digest(base)!=row['base_sha256']:
                raise RuntimeError('원본 게임 리소스가 일치하지 않습니다.')
            delta=decoder.zlib.decompress(raw)
            if row['kind']=='image_delta':
                canonical=decoder.canonical_png(pg,base,scratch,str(i))
                if decoder.digest(canonical)!=row['base_canonical_sha256']:
                    raise RuntimeError('원본 이미지 형식이 지원 빌드와 다릅니다.')
                restored=decoder.xor_bytes(canonical,delta,len(delta))[:row['target_canonical_size']]
                if decoder.digest(restored)!=row['target_canonical_sha256']:
                    raise RuntimeError('한국어 이미지 복원 검사에 실패했습니다.')
                raw=decoder.compact_png(restored)
            elif row['kind']=='video_delta':
                if len(delta)!=row['target_size']:raise RuntimeError('영상 차이 데이터 크기가 다릅니다.')
                raw=decoder.xor_bytes(base[:len(delta)],delta,len(delta))
            else:raise RuntimeError('지원하지 않는 패치 리소스입니다.')
            if decoder.digest(raw)!=row['output_sha256']:
                raise RuntimeError('한국어 리소스 복원 검사에 실패했습니다.')
            outputs[row['path']]=raw
    # Verify everything before modifying a resource. Restore any overwritten loose files on error.
    original={};written=[]
    try:
        for rel,raw in outputs.items():
            dst=decoder.contained(game/'game',rel)
            original[rel]=dst.read_bytes() if dst.exists() else None
            dst.parent.mkdir(parents=True,exist_ok=True)
            fd,temporary=tempfile.mkstemp(prefix='.ko_',dir=dst.parent)
            try:
                with os.fdopen(fd,'wb') as f:f.write(raw)
                os.replace(temporary,dst)
            finally:
                if os.path.exists(temporary):os.unlink(temporary)
            written.append(rel)
        stamp.write_text(json.dumps({'signature':signature,'version':manifest['version']},ensure_ascii=False),'utf8')
    except BaseException:
        for rel in reversed(written):
            dst=decoder.contained(game/'game',rel)
            if original[rel] is None:dst.unlink(missing_ok=True)
            else:dst.write_bytes(original[rel])
        raise
    return True
