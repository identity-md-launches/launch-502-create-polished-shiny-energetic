# Offline imaging runtime

`pillow-12.3.0-cp314-linux-x86_64-runtime.tar.xz` is a compact Pillow 12.3.0
runtime for the supplied CPython 3.14 / Linux x86_64 environment. It is an
ordinary checked-in archive, extracted by `../bootstrap.py` into disposable
`test/scratch/`. Rendering needs no pip, network access, or NumPy.

The archive retains every upstream Python module, the imaging, FreeType and
WebP native engines, and every bundled library transitively linked by those
engines. RGB/RGBA PNG and JPEG, lossless WebP, compositing, resampling, filters,
and variable-font text rendering are supported. Standard Linux libc, libm,
libdl, libpthread and zlib remain platform requirements, as in the source wheel.

To meet the source upload limit, unused AVIF, color-management, Tk, morphology
and image-math native engines are omitted. Debug and unneeded ELF symbols are
stripped. These optional engines are not used by this film; this archive is not
a full replacement for every Pillow feature. Python source and imaging
algorithms are unchanged. The original full Pillow/third-party license text
is preserved inside `pillow-12.3.0.dist-info/licenses/LICENSE`, along with
upstream package metadata. No license notice has been removed.

`manifest.json` records the upstream wheel identity, archive checksum and every
retained file. `repack.py` reproducibly creates the archive from that exact local
wheel using Python's standard library and GNU `strip`; it is not needed for
normal editing or rendering. The original wheel is deliberately not duplicated
in the upload. Other operating systems/Python ABIs need a compatible existing
Pillow installation.
