from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse
from itertools import groupby
from pathlib import Path
import shutil
import shlex
import subprocess

from . import forms
from .models import Think
from .random_slug import random_slug

class ThinkMixin(LoginRequiredMixin):
    model = Think
    context_object_name = 'think'

class IndexView(ThinkMixin, generic.ListView):
    template_name = 'thinks/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['templates'] = Think.objects.filter(is_template=True)

        context['thinks'] = sorted(Think.objects.filter(is_template=False), key=lambda t: (t.category if t.category else '', -t.creation_time.timestamp()))

        return context

class CreateThinkView(ThinkMixin, generic.CreateView):
    template_name = 'thinks/new.html'
    form_class = forms.CreateThinkForm

class RemixThinkView(ThinkMixin, generic.UpdateView):
    template_name = 'thinks/remix.html'
    form_class = forms.RemixThinkForm

    def dispatch(self, request, *args, **kwargs):
        if 'referer' in request.headers:
            return super().dispatch(request, *args, **kwargs)

        return self.do_remix()

    def form_valid(self, form):
        return self.do_remix()

    def do_remix(self):
        slug = self.kwargs['slug']
        nslug = random_slug()
        while (settings.THINKS_DIR / nslug).exists():
            nslug = random_slug()
        source = Think.objects.get(slug=slug)
        think = Think.objects.create(slug=nslug)
        shutil.copytree(source.root, think.root)

        return redirect(think.get_absolute_url())


class ThinkView(ThinkMixin, generic.DetailView):
    template_name = "thinks/think.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        think = self.object

        root = think.root

        strpath = self.request.GET.get('path')

        path = think.file_path(strpath)

        relpath = path.relative_to(root) if path is not None else None

        if path is None:
            directory = root
        elif path.is_dir():
            directory = path
        else:
            directory = path.parent

        files = [{'name': p.name, 'path': str(p.relative_to(root)), 'is_dir': p.is_dir()} for p in directory.iterdir()]
        if directory != root:
            files.insert(0, {'name': '..', 'path': str(directory.parent.relative_to(root)), 'is_dir': True})

        if path is not None and path.is_file():
            with open(path) as f:
                content = f.read()
        else:
            content = ''

        context['think_editor_data'] = {
            'preview_url': think.get_static_url(),
            'slug': think.slug,
            'files': files,
            'file_path': str(relpath),
            'file_content': content,
            'is_dir': path is None or path.is_dir(),
            'no_preview': self.request.GET.get('no-preview') is not None,
        }

        return context

class RenameThinkView(ThinkMixin, generic.UpdateView):
    form_class = forms.RenameThinkForm
    template_name = 'thinks/rename.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['categories'] = sorted(Think.objects.exclude(category=None).order_by('category').values_list('category',flat=True).distinct())

        return context

class DeleteThinkView(ThinkMixin, generic.DeleteView):
    template_name = 'thinks/delete.html'

    def get_success_url(self):
        return reverse('index')

class ReadFileView(ThinkMixin, generic.DetailView):
    def get(self, request, *args, **kwargs):
        think = self.get_object()
        relpath = self.kwargs['path']
        path = think.root / relpath
        print(path)


class SaveFileView(ThinkMixin, generic.UpdateView):
    form_class = forms.SaveFileForm
    template_name = 'thinks/save_file.html'

    def form_valid(self, form):
        self.path = form.cleaned_data['path'].relative_to(self.object.root)
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()+'?path='+str(self.path)

class RenameFileView(ThinkMixin, generic.UpdateView):
    form_class = forms.RenameFileForm
    template_name = 'thinks/rename_file.html'

    def form_valid(self, form):
        self.path = form.cleaned_data['newpath'].relative_to(self.object.root)
        print(form)
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()+'?path='+str(self.path)

class DeleteFileView(ThinkMixin, generic.UpdateView):
    form_class = forms.DeleteFileForm
    template_name = 'thinks/delete_file.html'

    def form_valid(self, form):
        self.path = form.cleaned_data['path'].relative_to(self.object.root)
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()+'?path='+str(self.path.parent)

class RunCommandView(ThinkMixin, generic.UpdateView):
    form_class = forms.RunCommandForm

    def form_valid(self, form):
        think = self.object
        command = form.cleaned_data['command']
        res = subprocess.run(
            ['bash','-c',command],
            cwd=think.root,
            encoding='utf8',
            capture_output=True
        )
        return JsonResponse({'stdout': res.stdout, 'stderr': res.stderr})

class LogView(ThinkMixin, generic.DetailView):
    template_name = 'thinks/think.html'

    def get(self, *args, **kwargs):
        think = self.get_object()

        return HttpResponse(think.get_log(), content_type='text/plain; charset=utf-8')
