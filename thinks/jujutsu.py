import functools
import subprocess
from django.conf import settings

def ensure_jj(fn):
    @functools.wraps(fn)
    def ofn(self,*args,**kwargs):
        self.init_jj()
        return fn(self,*args,**kwargs)

    return ofn

class JJController:
    def __init__(self, think):
        self.think = think
        self.root = think.root

    def run(self, cmd, **kwargs):
        print("Run command",cmd)
        res = subprocess.run(
            cmd,
            cwd=self.root,
            encoding='utf8',
            capture_output=True,
            **kwargs
        )
        return res

    def init_jj(self):
        print("Init jj")
        if not (self.root / '.jj').exists():
            self.run(['jj','git','init'])
            self.ignore_paths(['.make.*'])
            git_url = settings.GIT_REPO_URL_TEMPLATE.format(name=self.think.slug)
            self.run(['jj','git','remote','add','origin', git_url])

    @ensure_jj
    def status(self):
        res = self.run(['jj','st'])

        return res.stdout

    def clean_paths(self, paths):
        paths = [self.root / p for p in paths]
        return [str(p.relative_to(self.root)) for p in paths if p.is_relative_to(self.root)]

    @ensure_jj
    def ignore_paths(self, paths):
        paths = self.clean_paths(paths)
        gitignore = self.root / '.gitignore'
        if len(paths) == 0:
            return

        if gitignore.exists():
            with open(gitignore) as f:
                ignored = f.read().strip().split('\n')
            ignored += [p for p in paths if p not in ignored]
        else:
            ignored = paths

        with open(gitignore, 'w') as f:
            f.write('\n'.join(ignored))

    @ensure_jj
    def remove_paths(self, paths):
        paths = self.clean_paths(paths)
        if len(paths) == 0:
            return

        return self.run(['git','rm'] + paths)

    @ensure_jj
    def add_paths(self, paths):
        paths = self.clean_paths(paths)
        if len(paths) == 0:
            return

        return self.run(['git','add'] + paths)

    @ensure_jj
    def commit(self, message):
        res = self.run(['jj','describe','--stdin','--no-edit'], input=message)
        if res.returncode == 0:
            self.run(['jj','new'])
        return res
