# import pymysql
import json
import datetime
from django.http import JsonResponse
from django.test import TestCase
from django.db import connection
# from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from app01.utils.encrypt import md5

from django.shortcuts import render, redirect
from app01 import models
from app01.utils.bootstrap import BootStrapModelForm
from django.db.utils import OperationalError


class UserForm(BootStrapModelForm):
    # conform_password = forms.CharField(label="确认密码")    # 创建字段

    class Meta:
        model = models.User  # models.py 中的类名
        # fields = ["name", "gender", "password", "create_time", "quit_time", "depart"]
        # fields = ["name", "gender", "password", "conform_password", "create_time", "quit_time", "depart"]
        exclude = ["password"]

    # 钩子方法：
    def clean_name(self):
        txt_name = self.cleaned_data["name"]  # 用户传入的name数据
        if len(txt_name) < 2:  # 小于2个汉字或2个字符
            raise ValidationError("请正确输入名称")
        return txt_name


class WarehousingForm(BootStrapModelForm):
    class Meta:
        model = models.Warehousing  # models.py 中的类名
        fields = [
            "warehousing_date", "warehousing_name",
            "supplier", "quantity", "unit_price", "price"
        ]


# -------------- 测试 -------------- #
@csrf_exempt
def index_test05(request):
    """测试-05"""
    print(request.POST)
    data_dict = {"status": True}

    now_date = timezone.localdate()
    some_date = datetime.date(2023, 2, 13)
    queryset_n = models.Warehousing.objects.filter(warehousing_date=now_date)
    queryset_s = models.Warehousing.objects.filter(warehousing_date=some_date).count()
    # for item in queryset_s:
    #     print(['price'])
    print(now_date, some_date, queryset_n)

    now_date = timezone.localdate()
    quantity_num = models.Warehousing.objects.filter(warehousing_name=1).aggregate(Sum('quantity'))
    print(quantity_num)
    num = quantity_num['quantity__sum']
    print(num)
    if not num:
        return HttpResponse('有数据')
    return HttpResponse('无数据')
    now_time = timezone.localdate()
    print(now_time)

    obj = models.User.objects.filter(id=1)[0]
    print(obj.name, obj.password, obj.gender, obj.create_time)

    number = models.User.objects.count()
    print('员工人数：', number)
    return JsonResponse(data_dict)


def index_test01(request):
    """测试-01"""

    return render(request, 'test01.html')


def index_test02(request):
    """测试-02    """
    data_dict = {}
    verb = '咖'
    data_dict["warehousing_name__name__contains"] = verb
    queryset = models.Warehousing.objects.filter(**data_dict)
    form = WarehousingForm
    return render(request, "test02.html", {"queryset": queryset, "form": form})


def index_test03(request):
    """测试-03 批量修改数据 """
    models.Inventory.objects.filter(inventoryDate='2023-03-04').update(inventoryDate='2023-02-01')
    return render(request, "test03.html")


def index_test04():
    """测试-04"""

    models.Warehousing.objects.all().extra(
        select={'quantity': 'price > 20'}
    )

    return HttpResponse('完成测试')


def index_test06():
    queryset = models.Admin.objects.first()

# -------------- 测试 end --------------
