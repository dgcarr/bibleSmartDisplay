import hashlib
from pathlib import Path
for path in Path('artifacts').iterdir():
    if path.is_file() and path.suffix != '.sha256':
        path.with_name(path.name + '.sha256').write_text(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name + '\n')
