"""Verify preserved source bytes and the active canonical source inventory.

This checks source preservation only, not installation or hardware acceptance.
Pass --release-assets to verify the re-downloaded preserved attachments too.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

INVENTORY = 'records/adaptations-consolidation-20261104-inventory.json'
SOURCE_COMMIT = '373fe5506877c970a3fea89d5cf0614332d78d6f'


def member(root, name):
    if (not isinstance(name, str) or not name or '\\' in name or ':' in name
            or PurePosixPath(name).is_absolute() or any(x in ('', '.', '..') for x in name.split('/'))):
        raise ValueError('Unsafe preservation member')
    target = Path(root)
    for part in name.split('/'):
        target = target / part
        if target.is_symlink() or getattr(target, 'is_junction', lambda: False)():
            raise ValueError('Linked preservation member')
    return target


def check_bytes(path, row):
    raw = path.read_bytes()
    if len(raw) != row['size'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
        raise ValueError('Preserved bytes differ: ' + str(path))


def verify(root, *, old_source=None, release_assets=None):
    root = Path(root)
    inventory = json.loads(member(root, INVENTORY).read_bytes())
    if inventory.get('schema_version') != 1 or inventory.get('source_commit') != SOURCE_COMMIT:
        raise ValueError('Unexpected consolidation source')
    rows = inventory['files']
    if len(rows) != 500 or len({r['path'] for r in rows}) != 500:
        raise ValueError('Incomplete or duplicate historical inventory')
    if old_source is not None:
        def git(*args):
            return subprocess.check_output(['git', '-c', 'safe.directory=' + str(Path(old_source).resolve()),
                                           '-C', str(old_source), *args], stderr=subprocess.PIPE)
        names = set(git('ls-tree', '-r', '--name-only', SOURCE_COMMIT).decode().splitlines())
        if names != {r['path'] for r in rows}:
            raise ValueError('Historical inventory does not cover the original Git tree')
        for row in rows:
            raw = git('show', SOURCE_COMMIT + ':' + row['path'])
            if len(raw) != row['size'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
                raise ValueError('Historical inventory differs from original Git bytes')
    archived = existing = attachments = 0
    for row in rows:
        member(root, row['path'])  # Validate historical path syntax as well.
        state = row['disposition']
        if state == 'existing-byte-match':
            names = row['identical_canonical_paths']
            if not names:
                raise ValueError('Missing canonical preservation path')
            for name in names:
                check_bytes(member(root, name), row)
            existing += 1
        elif state == 'archived-byte-for-byte':
            check_bytes(member(root, row['archive_path']), row)
            archived += 1
        elif state == 'verified-immutable-release-attachment':
            expected = ('https://github.com/FlightDan/Boiler-adaptations/releases/download/'
                        'preserved-resources-20261104.1/input-source-r5.tar.gz')
            if row.get('url') != expected:
                raise ValueError('Unexpected preservation attachment URL')
            if release_assets is not None:
                check_bytes(member(release_assets, 'input-source-r5.tar.gz'), row)
            attachments += 1
        else:
            raise ValueError('Unpreserved source member: ' + row['path'])
    proof = json.loads(member(root, 'records/release-preservation-proof-20261104.json').read_bytes())
    if (proof.get('repository_id') != 1430004734 or proof.get('retiring_repository_id') != 1440878758
            or proof.get('retiring_source_commit') != SOURCE_COMMIT
            or proof.get('preserved_release') != 'preserved-resources-20261104.1'
            or len(proof.get('assets', [])) != 4):
        raise ValueError('Unexpected preserved release proof')
    if release_assets is not None:
        for row in proof['assets']:
            check_bytes(member(release_assets, row['name']), row)
    active = json.loads(member(root, 'model-source-files.json').read_bytes())
    if active.get('kind') != 'CanonicalAdaptationSourceFiles' or active.get('schema_version') != 1:
        raise ValueError('Unexpected active source inventory')
    names = set()
    for row in active['files']:
        name = row['path']
        if name in names or any(p.casefold() in ('.git', '.local', '.codex', '.agents', '.aws') for p in name.split('/')):
            raise ValueError('Duplicate or private active source member')
        if name.startswith('records/legacy-adaptations-373fe55/objects/'):
            raise ValueError('Historical objects cannot be active build inputs')
        names.add(name)
        check_bytes(member(root, name), row)
    required = {'brands/onexplayer/oxp3/oxp3.toon', 'brands/onexplayer/x2-mini/x2-mini.toon'}
    if not required <= names:
        raise ValueError('Missing canonical model TOON')
    return dict(historical_files=len(rows), existing=existing, archived=archived,
                attachments=attachments, preserved_release_assets=len(proof['assets']),
                attachment_bytes_verified=release_assets is not None,
                active_files=len(names), source_preservation_only=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--old-source-checkout', type=Path)
    parser.add_argument('--release-assets', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root, old_source=args.old_source_checkout,
                            release_assets=args.release_assets), indent=2))
