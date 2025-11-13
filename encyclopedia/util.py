import re
from django.core.files.base import ContentFile
from .storage import entry_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = entry_storage.listdir("")
    return list(sorted(
        re.sub(r"\.md$", "", filename)
        for filename in filenames
        if filename.endswith(".md")
    ))


def save_entry(title, content):
    """
    Saves an encyclopedia entry using local app storage.
    """
    filename = f"{title}.md"
    if entry_storage.exists(filename):
        entry_storage.delete(filename)
    entry_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title.
    """
    try:
        f = entry_storage.open(f"{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None
