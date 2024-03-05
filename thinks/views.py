from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse
from pathlib import Path
import shutil
import subprocess

from . import forms
from .models import Think
from .random_slug import random_slug

class ThinkMixin(LoginRequiredMixin):
    model = Think
    context_object_name = 'think'

class IndexView(ThinkMixin, generic.ListView):
    template_name = 'thinks/index.html'

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
    template_name = 'thinks/think.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        think = self.object

        strpath = self.request.GET.get('path')

        path = think.file_path(strpath)

        relpath = path.relative_to(think.root) if path is not None else None

        if path is None:
            directory = think.root
        elif path.is_dir():
            directory = path
        else:
            directory = path.parent

        files = [(p.name, p.relative_to(think.root)) for p in directory.iterdir()]
        if directory != think.root:
            files.insert(0, ('..', directory.parent.relative_to(think.root)))
        context['files'] = files

        context['directory'] = directory

        context['path'] = relpath

        if path is not None and path.is_file():
            with open(path) as f:
                content = f.read()
        else:
            content = ''

        context['content'] = content

        context['file_form'] = forms.SaveFileForm(instance=think, initial={'content': content, 'path': relpath})

        return context

class RenameThinkView(ThinkMixin, generic.UpdateView):
    form_class = forms.RenameThinkForm
    template_name = 'thinks/rename.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

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
            command.split(' '),
            cwd=think.root,
            encoding='utf8',
            capture_output=True
        )
        return JsonResponse({'stdout': res.stdout, 'stderr': res.stderr})
