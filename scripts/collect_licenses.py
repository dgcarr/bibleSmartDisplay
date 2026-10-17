"""Copy installed dependency licence notices into the binary distribution."""
from importlib.metadata import distribution
from pathlib import Path
import shutil

for name in ('Pillow', 'pyserial', 'filelock', 'pyinstaller', 'smartscreen-driver', 'numpy', 'PySide6', 'PySide6_Essentials', 'PySide6_Addons', 'shiboken6'):
    try:
        dist = distribution(name)
    except Exception:
        if name in ('PySide6', 'PySide6_Essentials', 'PySide6_Addons', 'shiboken6'):
            continue
        raise
    target = Path('dist/licenses') / name
    target.mkdir(parents=True, exist_ok=True)
    (target / 'METADATA.txt').write_text(dist.read_text('METADATA') or '', encoding='utf-8')
    for entry in dist.files or []:
        if any(word in str(entry).lower() for word in ('license', 'copying', 'notice')):
            source = Path(dist.locate_file(entry))
            if source.is_file():
                shutil.copy2(source, target / source.name)
