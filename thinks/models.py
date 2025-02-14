from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.timezone import datetime, make_aware

from .jujutsu import JJController

THINKS_DIR = settings.THINKS_DIR

# Create your models here.
class Think(models.Model):

    slug = models.SlugField()
    category = models.CharField(max_length=100, blank=True, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)

    is_template = models.BooleanField(default=False)

    class Meta:
        ordering = ('slug',)

    @property
    def root(self):
        return (THINKS_DIR / self.slug).resolve()

    @property
    def jj_controller(self):
        return JJController(self)

    def has_jj(self):
        return (self.root / '.jj').exists()

    def get_absolute_url(self):
        return reverse('think', kwargs={'slug': self.slug})

    def get_static_url(self):
        return settings.THINKS_STATIC_URL.format(slug=self.slug)

    def files(self):
        for f in self.root.iterdir():
            yield f.relative_to(self.root)

    def file_path(self, relpath):
        if relpath is None:
            return None
        path = (self.root / relpath).resolve()
        if not path.is_relative_to(self.root):
            raise Exception(f"Bad path {path}")
        return path

    def get_readme(self):
        readme_path = self.file_path('README')
        for suffix in ['', '.md', '.rst', '.txt']:
            p = readme_path.with_suffix(suffix)
            if p.exists():
                with open(p) as f:
                    return f.read()

        return None

    def get_log(self):
        log_file = self.file_path('.make.log')
        if not log_file.exists():
            return ''
        
        with open(log_file) as f:
            log = f.read()

        return log

    def as_json(self):
        return {
            'slug': self.slug,
            'category': self.category,
            'absolute_url': self.get_absolute_url(),
            'readme': self.get_readme(),
            'creation_time': self.creation_time,
        }
