from django.core.files.storage import FileSystemStorage

ENTRIES_PATH = r"encyclopedia/entries"

entry_storage = FileSystemStorage(location=ENTRIES_PATH)
