from django.shortcuts import render, get_object_or_404, redirect
from markdown import Markdown
from django import forms
from . import util
from django.http import HttpResponseRedirect
import random
from django.urls import reverse



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchEntryForm()
    })

# Render entry page
def entry(request, name):
    entry_content = util.get_entry(name)
    markdowner = Markdown()
    if entry_content:
        content = markdowner.convert(entry_content)
    else:
        content = None

    if entry_content:
        return render(request, "encyclopedia/entry.html",  {
            "title": name.title(),
            "content": content,
            "search_form": SearchEntryForm()
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "This entry was not found.",
            "search_form": SearchEntryForm()
        })
    

# Create a class to input new markdown file
class NewMarkdownFile(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))


# Create a function to new md file
def newpage(request):
    entries = util.list_entries()

    if request.method == "POST":
        form = NewMarkdownFile(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]  # no need to encode here

            # Check if entry exists (case-insensitive)
            for entry in entries:
                if title.lower() == entry.lower():
                    return render(request, "encyclopedia/error.html", {
                        "exist_error": "This entry already exists.",
                        "search_form": SearchEntryForm()
                    })

            # Save entry
            util.save_entry(title, content)
            return redirect("encyclopedia:entry", name=title)

        else:
            return render(request, "encyclopedia/newpage.html", {
                "form": form,
                "search_form": SearchEntryForm()
            })

    else:
        form = NewMarkdownFile()
        return render(request, "encyclopedia/newpage.html", {
            "form": form,
            "search_form": SearchEntryForm()
        })
 
# Random page function
def randompage(request):
    names = util.list_entries()
    if not names:
        # Graceful fallback if there are no entries
        return redirect("encyclopedia:index")

    name = random.choice(names)

    # Option 1 – using redirect with URL name:
    return redirect("encyclopedia:entry", name=name)


# Create a class to search form
class SearchEntryForm(forms.Form):
    # search = forms.CharField(max_length=100)
    search_entry = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control-search',
        'placeholder': 'Search page',
        }),
        label='')
    
# Search function to render the page
def search(request):
    result = []
    entries = util.list_entries()
    # Check if method is POST
    if request.method == "POST":
        # Take user's data search
        search_form = SearchEntryForm(request.POST)
        # Check if form is valid
        if search_form.is_valid():
            search_entry = search_form.cleaned_data["search_entry"]
            for entry in entries:
                if search_entry.lower() == entry.lower():
                    return HttpResponseRedirect(f"{search_entry}")
                # Code above here is okay

            # Check letters in entry's name
            for entry in entries:
                if search_entry.lower() in entry.lower():
                    result.append(entry)

            # Render search results if there are partial matches
            if result:
                return render(request, "encyclopedia/search.html", {
                    "search_form": SearchEntryForm(),
                    "entries": result,
                    "search_entry": search_entry.lower()
                })

            # If no matches, show error
            return render(request, "encyclopedia/error.html", {
                "message": "This entry was not found.",
                "search_form": SearchEntryForm()
            })

    # If GET method, show index page
    return render(request, "encyclopedia/index.html", {
        "search_form": SearchEntryForm()
    })


def edit_entry(request, name):
    # Fetch the entry content
    entry_content = util.get_entry(name)

    if entry_content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "This entry does not exist.",
            "search_form": SearchEntryForm()
        })

    if request.method == "POST":
        # Process the form submission
        form = NewMarkdownFile(request.POST)
        if form.is_valid():
            # Get updated content
            updated_content = form.cleaned_data["content"].encode('utf-8')
            # Create a entry copy changing title(name)
            name = form.cleaned_data['title']            
            # Save updated entry
            util.save_entry(name, updated_content)
            # Redirect to the updated entry page
            return HttpResponseRedirect(f"/wiki/{name}")
    # If GET, prefill the form with the current content
    else:
        form = NewMarkdownFile(initial={"title": name, "content": entry_content})

    return render(request, "encyclopedia/edit.html", {
        "form": form,
        "title": name,
        "search_form": SearchEntryForm()
    })
