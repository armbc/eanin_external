from django.shortcuts import render


# -------------- 首页 -------------- #
def index(request):
    """首页"""
    return render(request, "index.html")
# -------------- 首页end -------------- #
