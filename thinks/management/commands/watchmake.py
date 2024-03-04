"""
Requires the ``watchdog`` package.

Watch the current directory and its children for changes to files, and run ``make`` when certain files are changed.

Can be configured by a .watchmakerc file, containing settings in YAML format:

    path = <the path to watch for changes> (default: .)
    default_make: <a list of `make` targets to run> (default: empty list, so the first target in the Makefile)
    extensions: <a list of file extensions that should trigger a ``make`` run> (default: '.js')
"""

from copy import deepcopy
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from datetime import datetime
import os
import subprocess
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml
from pathlib import Path

class MakeHandler(FileSystemEventHandler):

    last_time = None
    gap = 2

    extensions = None

    default_config = {
        'path': '.',
        'default_make': [],
        'extensions': ['.js'],
    }

    def __init__(self, root):
        super().__init__()

        self.configs = {}

        self.root = root.resolve()

    def get_think_root(self, d):
        while d.parent != self.root:
            d = d.parent

        return d

    def get_config(self, p):
        d = self.get_think_root(p)

        if d not in self.configs:
            self.load_config(d)

        return self.configs[d]

    def load_config(self, d):
        print(f"Fetch config for {d}")
        
        config_path = d / '.watchmakerc'

        config = deepcopy(self.default_config)
        if config_path.exists():
            with open(config_path) as f:
                config.update(yaml.load(f.read(),Loader=yaml.SafeLoader))

        self.configs[d] = config

    def on_modified(self, event):
        root = self.root

        if event.is_directory:
            return
    
        t = datetime.now()

        src_path = Path(event.src_path).resolve()

        if self.extensions is None or src_path.suffix in self.extensions:
            if not src_path.is_relative_to(root.resolve()):
                return
        
            print('{} modified at {}'.format(root / src_path.relative_to(root.resolve()),t))

            if src_path.name == '.watchmakerc' or (self.last_time is None or (t-self.last_time).seconds > self.gap):
                self.run(src_path)

            self.last_time = t

    def run(self, p):
        d = self.get_think_root(p)
        print(f"Run for {d}")
        print(p.name)
        if p.name == '.watchmakerc':
            self.load_config(d)
        config = self.get_config(p)
        print(config)

        if (d / 'Makefile').exists():
            print("Making")
            command = ['make'] + config.get('default_make', [])
            res = subprocess.run(command, cwd=d, capture_output=True, encoding='utf-8')
            with open(d / '.make.log', 'w') as f:
                f.write(res.stdout)
                f.write(res.stderr)
        else:
            print("No make")

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.rootpath = settings.THINKS_DIR

        self.run()

    def run(self,targets=None):
        print(f"Watching {self.rootpath}")

        event_handler = MakeHandler(self.rootpath)

        observer = Observer()
        observer.schedule(event_handler,str(self.rootpath),recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()

