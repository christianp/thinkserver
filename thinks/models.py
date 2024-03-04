from django.conf import settings
from django.db import models
from django.urls import reverse

THINKS_DIR = settings.THINKS_DIR

# Create your models here.
class Think(models.Model):

    slug = models.SlugField()

    class Meta:
        ordering = ('slug',)

    @property
    def root(self):
        return (THINKS_DIR / self.slug).resolve()

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
