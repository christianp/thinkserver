from django import forms
from django.conf import settings

from .models import Think

class CreateThinkForm(forms.ModelForm):
    class Meta:
        model = Think
        fields = ['slug']
    
    def save(self, commit=True):
        print("SAVE", commit)
        instance = super().save(commit)
        if commit:
            instance.root.mkdir(exist_ok=True,parents=True)
        return instance

class RemixThinkForm(forms.ModelForm):
    class Meta:
        model = Think
        fields = []

class RenameThinkForm(forms.ModelForm):
    class Meta:
        model = Think
        fields = ['slug', 'category', 'is_template']
        widgets = {
            'category': forms.TextInput(attrs={'list': 'categories'})
        }

    def __init__(self, *args, instance=None, **kwargs):
        self.original_root = None if instance is None else instance.root
        super().__init__(*args, instance=instance, **kwargs)

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        root = settings.THINKS_DIR / slug
        if root.exists() and slug != self.instance.slug:
            raise forms.ValidationError("A think with the slug {slug} already exists")

        return slug
    
    def save(self, commit=True):
        slug = self.cleaned_data['slug']
        root = settings.THINKS_DIR / slug

        self.original_root.rename(root)

        instance = super().save(commit)
        return instance

class SaveFileForm(forms.ModelForm):
    path = forms.CharField()
    content = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Think
        fields = []
    
    def clean_path(self):
        return self.instance.file_path(self.cleaned_data['path'])

    def save(self, commit=False):
        path = self.cleaned_data['path']
        content = self.cleaned_data['content']

        if not path.parent.exists():
            path.parent.mkdir(exist_ok=True, parents=True)

        with open(path, 'w') as f:
            f.write(content)

        return super().save(commit)

class RenameFileForm(forms.ModelForm):
    path = forms.CharField()
    newpath = forms.CharField()

    class Meta:
        model = Think
        fields = []
    
    def clean_path(self):
        path = self.instance.file_path(self.cleaned_data['path'])
        return path

    def clean_newpath(self):
        path = self.instance.file_path(self.cleaned_data['newpath'])
        if path.exists():
            raise forms.ValidationError("The file {path} already exists")
        return path

    def save(self, commit=False):
        oldpath = self.cleaned_data['path']
        newpath = self.cleaned_data['newpath']

        print(oldpath,">",newpath)

        oldpath.rename(newpath)        

        return super().save(commit)

class DeleteFileForm(forms.ModelForm):
    path = forms.CharField()

    class Meta:
        model = Think
        fields = []
    
    def clean_path(self):
        path = self.instance.file_path(self.cleaned_data['path'])
        if path == self.instance.root:
            raise forms.ValidationError("Can't delete the think's root")

        return path

    def save(self, commit=False):
        path = self.cleaned_data['path']

        path.unlink()

        return super().save(commit)

class RunCommandForm(forms.ModelForm):
    command = forms.CharField()

    class Meta:
        model = Think
        fields = []
