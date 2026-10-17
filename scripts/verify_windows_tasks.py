"""Exercise real Task Scheduler registration/removal on an isolated CI runner."""
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from desktop import core, scheduler

with tempfile.TemporaryDirectory(prefix='Bible task test ') as temp:
    root = Path(temp)
    with patch.object(scheduler, 'NAME', 'BibleSmartDisplayCITest'), patch.object(scheduler, 'command', return_value=[sys.executable, '-c', 'pass']):
        try:
            scheduler.configure(root, dict(core.DEFAULTS, scheduled=True, startup=True))
            for name in ('BibleSmartDisplayCITestDaily', 'BibleSmartDisplayCITestTray'):
                result = subprocess.run(['schtasks', '/Query', '/TN', name, '/XML'], check=True, capture_output=True, text=True)
                if 'InteractiveToken' not in result.stdout:
                    raise RuntimeError('Task is not restricted to the logged-in user')
        finally:
            scheduler.configure(root, dict(core.DEFAULTS))
        for name in ('BibleSmartDisplayCITestDaily', 'BibleSmartDisplayCITestTray'):
            if subprocess.run(['schtasks', '/Query', '/TN', name], capture_output=True).returncode == 0:
                raise RuntimeError('Task removal failed')
