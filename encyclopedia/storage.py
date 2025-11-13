from django.core.files.storage import FileSystemStorage
import os

ENTRIES_PATH = r"encyclopedia/entries"

entry_storage = FileSystemStorage(location=ENTRIES_PATH)
