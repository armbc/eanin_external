"""
本视图函数包括：
1、打印入库单单元
2、打印出库单单元
"""

from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from app01 import models
from django import forms
from django.core.exceptions import ValidationError
from app01.utils.bootstrap import BootStrapModelForm
from app01.utils.bootstrap import BootStrapForm


@csrf_exempt
def print_warehousing(request):
    return JsonResponse({"status": True})
