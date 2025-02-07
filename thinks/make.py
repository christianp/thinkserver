from datetime import datetime
from filelock import FileLock, Timeout
import subprocess
import yaml

class ThingMaker():

    gap = 2

    extensions = None

    config = {
        'path': '.',
        'default_make': [],
        'extensions': ['.js'],
    }

    def __init__(self, think):
        self.think = think
        self.load_config()


    def load_config(self,):
        config_path = self.think.root / '.watchmakerc'

        if config_path.exists():
            with open(config_path) as f:
                self.config.update(yaml.load(f.read(),Loader=yaml.SafeLoader))

        self.extensions = self.config.get('extensions')


    def make(self, file_changed):
        if file_changed.is_dir():
            return {"error": f"{file_changed} is directory"}

        root = self.think.root

        t = datetime.now()

        src_path = (root / file_changed).resolve()

        if not src_path.is_relative_to(root.resolve()):
            return {"error": f"{src_path} is not relative to root {root}"}
                
        if src_path.name == '.watchmakerc' or self.extensions is None or src_path.suffix in self.extensions:
            lock_path = str(root / '.make.lock')
            lock = FileLock(lock_path, timeout=5)

            try:
                with lock:
                    return self.run(src_path)
            except Timeout:
                return {"error": "Timed out"}


    def run(self, p):
        root = self.think.root
        if (root / 'Makefile').exists():
            command = ['make'] + self.config.get('default_make', [])
            res = subprocess.run(command, cwd=root, capture_output=True, encoding='utf-8')
            with open(root / '.make.log', 'w') as f:
                f.write(f"{datetime.now()}\n")
                f.write(res.stdout)
                f.write(res.stderr)

            return {
                'stdout': res.stdout,
                'stderr': res.stderr,
            }
        else:
            return {"error": "No make"}
