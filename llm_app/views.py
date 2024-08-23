from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse(
        '<header><h1>Hello this is the index page</h1></header><body><a href="http://127.0.0.1:8000/admin">Please click here for the Admin page</a></body>'
    )
