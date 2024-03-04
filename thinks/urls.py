from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('think/<slug:slug>', ThinkView.as_view(), name='think'),
    path('think/<slug:slug>/rename', RenameThinkView.as_view(), name='rename_think'),
    path('think/<slug:slug>/delete', DeleteThinkView.as_view(), name='delete_think'),
    path('think/<slug:slug>/file/<path:path>', ReadFileView.as_view(), name='read_file'),
    path('think/<slug:slug>/save-file', SaveFileView.as_view(), name='save_file'),
    path('think/<slug:slug>/rename-file', RenameFileView.as_view(), name='rename_file'),
    path('think/<slug:slug>/delete-file', DeleteFileView.as_view(), name='delete_file'),
    path('think/<slug:slug>/run-command', RunCommandView.as_view(), name='run_command'),
    path('new', CreateThinkView.as_view(), name='new_think'),
    path('new/<slug:slug>', RemixThinkView.as_view(), name='remix_think'),
]

