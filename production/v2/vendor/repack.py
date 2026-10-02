"""Reproduce the compact runtime from the exact upstream wheel, offline.

Only needed to audit/rebuild the dependency archive, not to render the film.
Usage: python production/v2/vendor/repack.py PATH_TO_ORIGINAL_PILLOW_WHEEL
Requires the supplied Python standard library and GNU strip.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import zipfile

UPSTREAM_SHA256 = '251bf95b67017e27b13d82f5b326234ca62d70f9cf4c2b9032de2358a3b12c7b'
LIBRARIES = (
    'libtiff-', 'libjpeg-', 'libopenjp2-', 'libxcb-', 'libzstd-', 'liblzma-',
    'libXau-', 'libfreetype-', 'libharfbuzz-', 'libpng16-', 'libbrotlidec-',
    'libbrotlicommon-', 'libwebp-', 'libwebpdemux-', 'libwebpmux-', 'libsharpyuv-',
)


def retain(name):
    path = Path(name)
    return (
        (name.startswith('PIL/') and path.suffix in ('.py', '.pyi'))
        or name.startswith(('PIL/_imaging.', 'PIL/_imagingft.', 'PIL/_webp.'))
        or (name.startswith('pillow.libs/') and path.name.startswith(LIBRARIES))
        or '/licenses/' in name
        or name.endswith('/METADATA')
    )


def main():
    original = Path(sys.argv[1])
    if hashlib.sha256(original.read_bytes()).hexdigest() != UPSTREAM_SHA256:
        raise ValueError('Expected the pinned upstream Pillow 12.3.0 wheel')
    vendor = Path(__file__).resolve().parent
    package = vendor / 'pillow-12.3.0-cp314-linux-x86_64-runtime.tar.xz'
    files = []
    with tempfile.TemporaryDirectory(prefix='pepe-pillow-repack-') as scratch:
        staging = Path(scratch)
        with zipfile.ZipFile(original) as wheel:
            for entry in wheel.infolist():
                if entry.is_dir() or not retain(entry.filename):
                    continue
                target = staging / entry.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(wheel.read(entry))
                if target.read_bytes()[:4] == b'\x7fELF':
                    subprocess.run(['strip', '--strip-unneeded', str(target)], check=True)
        with tarfile.open(package, 'w:xz', preset=9) as archive:
            for path in sorted(staging.rglob('*')):
                if not path.is_file():
                    continue
                name = path.relative_to(staging).as_posix()
                info = archive.gettarinfo(path, arcname=name)
                info.mtime = info.uid = info.gid = 0
                info.uname = info.gname = ''
                info.mode = 0o644
                with path.open('rb') as source:
                    archive.addfile(info, source)
                files.append({'path': name, 'bytes': path.stat().st_size,
                              'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {
        'archive': {'file': package.name, 'bytes': package.stat().st_size,
                    'sha256': hashlib.sha256(package.read_bytes()).hexdigest()},
        'upstream': {'file': original.name, 'sha256': UPSTREAM_SHA256,
                     'origin': 'https://pypi.org/project/pillow/12.3.0/'},
        'transformation': 'All Python modules, imaging/font/WebP engines, their complete '
                          'bundled shared-library closure, upstream metadata and full licenses. '
                          'Unused native engines removed; ELF debug/unneeded symbols stripped. '
                          'No Python source or image algorithms modified.',
        'files': files,
    }
    (vendor / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest['archive'], indent=2))


if __name__ == '__main__':
    main()
