from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from . import util
from random import randrange
from markdown2 import Markdown
markdowner = Markdown()


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(
        attrs={'placeholder': 'Title', 'class': 'form-control my-2', }))
    title_disabled = forms.CharField(required=False, disabled=True, label="Title", widget=forms.TextInput(
        attrs={'placeholder': 'Title', 'class': 'form-control my-2', }))
    body = forms.CharField(label="Content", widget=forms.Textarea(
        attrs={'placeholder': 'Content', 'class': 'form-control my-2'}))
    is_editing = forms.CharField(widget=forms.HiddenInput(), initial='False')


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry_title):
    entry_data = util.get_entry(entry_title)
    if entry_data != None:
        return render(request, "encyclopedia/entry.html", {
            "entry_content": markdowner.convert(util.get_entry(entry_title)),
            "entry_title": entry_title
        })
    else:
        return render(request, "encyclopedia/404.html", {
            "query": entry_title,
        })


def search(request):
    if request.method == "POST":
        query = request.POST['q']
        entry_data = util.get_entry(query)
        if entry_data != None:
            return HttpResponseRedirect(reverse('entry', args=[query]))
        else:
            list_entries = list(
                filter(lambda a: query.casefold() in a.casefold(), util.list_entries()))
            listLenght = len(list_entries)
            nothing_found = False
            if listLenght == 0:
                nothing_found = True
            return render(request, "encyclopedia/search.html", {
                "query": query,
                "entries": list_entries,
                "nothing_found": nothing_found
            })
    else:
        return HttpResponseRedirect(reverse('index'))


def new(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            body = form.cleaned_data["body"]
            is_editing = form.cleaned_data["is_editing"]
            entry_data = util.get_entry(title)
            if entry_data != None and is_editing == 'False':
                return render(request, "encyclopedia/new.html", {
                    "form": form,
                    "entry_exist": True,
                    "entry_title": title
                })
            else:
                util.save_entry(title, body)
                return HttpResponseRedirect(reverse('entry', args=[title]))
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form,
                "empty_input": form.errors
            })
    else:
        return render(request, "encyclopedia/new.html", {
            "form": NewEntryForm()
        })


def edit(request, entry_title):
    entry_data = util.get_entry(entry_title)
    form = NewEntryForm()
    form.fields['title'].widget = forms.HiddenInput()
    form.fields['is_editing'].initial = "True"
    form.fields['title_disabled'].initial = entry_title
    form.fields['title'].initial = entry_title
    form.fields['body'].initial = entry_data
    return render(request, "encyclopedia/new.html", {
        "form": form,
        "is_editing": True
    })


def random(request):
    number_of_pages = len(util.list_entries())
    random_number = randrange(0, number_of_pages)
    random_page_title = util.list_entries()[random_number]
    return HttpResponseRedirect(reverse('entry', args=[random_page_title]))
