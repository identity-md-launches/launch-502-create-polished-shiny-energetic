"""Load the bundled, compact Pillow runtime without pip or network access.

The bundled binaries target CPython 3.14 / Linux x86_64. Other platforms can
use an existing Pillow environment. Extraction stays in disposable scratch.
"""
from pathlib import Path
import hashlib
import json
import platform
import sys
import tarfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def setup():
    bundled_platform = (
        sys.implementation.name == 'cpython'
        and sys.version_info[:2] == (3, 14)
        and sys.platform == 'linux'
        and platform.machine() == 'x86_64'
    )
    if not bundled_platform:
        try:
            from PIL import Image, ImageFont
            return
        except ImportError as exc:
            raise RuntimeError(
                'The included Pillow runtime requires CPython 3.14 on Linux '
                'x86_64. On another platform, provide Pillow 12.3.0 locally.'
            ) from exc

    vendor = ROOT / 'production/v2/vendor'
    manifest = json.loads((vendor / 'manifest.json').read_text())
    package = vendor / manifest['archive']['file']
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    if digest != manifest['archive']['sha256']:
        raise RuntimeError('Bundled Pillow archive checksum mismatch')
    cache = ROOT / 'test/scratch' / ('v2-pillow-' + digest[:16])
    marker = cache / '.ready'
    if not marker.exists():
        cache.mkdir(parents=True, exist_ok=True)
        with tarfile.open(package, 'r:xz') as archive:
            archive.extractall(cache, filter='data')
        marker.write_text(digest + '\n')
    sys.path.insert(0, str(cache))


setup()
