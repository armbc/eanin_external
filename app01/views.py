import datetime
import datetime as dt
import os

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from openpyxl import load_workbook

from app01 import models
from app01.utils.bootstrap import BootStrapModelForm
from app01.utils.encrypt import md5


# -------------- 定义类(ModelForm) -------------- #
class DpartForm(BootStrapModelForm):
    class Meta:
        model = models.Department  # models.py 中的类名
        fields = ["name", "area"]
        # 添加Bootstrap样式:
        # widgets = {
        #     "name": forms.TextInput(attrs={"class": "form-control"}),
        #     "area": forms.TextInput(attrs={"class": "form-control"})
        # }


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


class MateForm(BootStrapModelForm):
    class Meta:
        model = models.Material  # models.py 中的类名
        fields = ["name", "category", "model", "guarantee_period", "unit"]

    # 钩子方法：
    def clean_name(self):
        txt_name = self.cleaned_data["name"]  # 用户传入的name数据
        exists = models.Material.objects.filter(name=txt_name).exists()  # 寻找数据库中同名的 name
        if exists:
            raise ValidationError("该物料已存在")
        return txt_name


class MateEditForm(BootStrapModelForm):
    # name = forms.CharField(disabled=True, label="名称")  # 不可编辑，但可以显示

    class Meta:
        model = models.Material  # models.py 中的类名
        fields = ["name", "category", "model", "guarantee_period", "unit"]

    # 钩子方法：
    def clean_name(self):
        # self.instance.pk    # 当前编辑行的 ID
        txt_name = self.cleaned_data["name"]  # 用户传入的name数据
        exists = models.Material.objects.exclude(id=self.instance.pk).filter(
            name=txt_name).exists()  # 寻找数据库中排除自己以外，同名的 name
        if exists:
            raise ValidationError("该物料已存在")
        return txt_name


class SupplierForm(BootStrapModelForm):
    # name = forms.CharField(disabled=True, label="名称")  # 不可编辑，但可以显示

    class Meta:
        model = models.Supplier  # models.py 中的类名
        fields = ["name", "address", "phone"]

    # 钩子方法：
    def clean_name(self):
        # self.instance.pk    # 当前编辑行的 ID
        txt_name = self.cleaned_data["name"]  # 用户传入的name数据
        exists = models.Supplier.objects.exclude(id=self.instance.pk).filter(
            name=txt_name).exists()  # 寻找数据库中排除自己以外，同名的 name
        if exists:
            raise ValidationError("该物料已存在")
        return txt_name


class SupplierEditForm(BootStrapModelForm):
    # name = forms.CharField(disabled=True, label="名称")  # 不可编辑，但可以显示

    class Meta:
        model = models.Supplier  # models.py 中的类名
        fields = ["name", "address", "phone"]

    # 钩子方法：
    def clean_name(self):
        # self.instance.pk    # 当前编辑行的 ID
        txt_name = self.cleaned_data["name"]  # 用户传入的name数据
        exists = models.Supplier.objects.exclude(id=self.instance.pk).filter(
            name=txt_name).exists()  # 寻找数据库中排除自己以外，同名的 name
        if exists:
            raise ValidationError("该供应商已存在")
        return txt_name


class WarehousingForm(BootStrapModelForm):
    class Meta:
        model = models.Warehousing  # models.py 中的类名
        fields = [
            "warehousing_date", "warehousing_name",
            "supplier", "quantity", "unit_price", "price"
        ]


class WarehousingChoiceForm(BootStrapModelForm):
    class Meta:
        model = models.Warehousing  # models.py 中的类名
        fields = [
            "warehousing_date", "supplier",
        ]


class WarehousingAddForm(BootStrapModelForm):
    class Meta:
        model = models.Warehousing  # models.py 中的类名
        fields = [
            "warehousing_date", "quantity", "warehousing_name",
            "price", "supplier", "produceDate"
        ]
        widgets = {
            "warehousing_name": forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true",
                       "data-size": "10", "data-header": "搜索关键字："}),
            "supplier": forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true",
                       "data-size": "10", "data-header": "搜索关键字："})
        }


# -------------- 定义类end -------------- #


# -------------- 首页 -------------- #
def index(request):
    """首页"""
    return render(request, "index.html")
# -------------- 首页end -------------- #


# -------------- 部门管理 -------------- #
def ai_list01(request):
    return render(request, "ai_list01.html")


def depart_list01(request):
    form = DpartForm()
    queryset = models.Department.objects.all()
    return render(request, "depart_list01.html", {'form': form, 'queryset': queryset})


def depart_edit01(request, nid):
    # nid = request.GET.get('nid')
    row_object = models.Department.objects.filter(id=nid).first()
    if request.method == 'GET':
        form = DpartForm(instance=row_object)
        return render(request, 'depart_edit01.html', {'form': form})
    form = DpartForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/depart/list01/')
    return render(request, 'depart_list01.html', {"form": form})


def depart_add01(request):
    """添加部门（ModelForm版本）"""
    title = "添加部门"
    if request.method == "GET":
        form = DpartForm()
        return render(request, "add_model.html", {'form': form, "title": title})
    # 校验数据是否合法：
    form = DpartForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/depart/list01/')
    # 校验失败：
    return render(request, 'add_model.html', {"form": form, "title": title})


def depart_delete01(request):
    """ 删除部门 """

    uid = request.GET.get('uid')
    exists = models.Department.objects.filter(id=uid).exists()
    if not exists:
        return JsonResponse({"status": False, 'error': "数据不存在,删除失败"})
    models.Department.objects.filter(id=uid).delete()
    return JsonResponse({"status": True})


# -------------- 员工管理 -------------- #
def user_list01(request):
    form = UserForm()
    queryset = models.User.objects.all()
    return render(request, "user_list01.html", {'form': form, 'queryset': queryset})


def user_add01(request):
    """ 增加用户 """
    title = '新增用户'
    creat_time = '#id_create_time'
    quit_time = '#id_quit_time'
    if request.method == "GET":
        form = UserForm()
        return render(request, 'add_model.html', {
            "form": form, "title": title, "creat_time": creat_time, "quit_time": quit_time
        })
    # 校验数据是否合法：
    form = UserForm(data=request.POST)
    if form.is_valid():
        # 数据合法，ModelForm用简单的语句，将所有数据保存到数据库
        pwd = md5("123456")
        form.instance.password = pwd
        form.save()
        return redirect('/user/list01/')
    # 校验失败：
    return render(request, 'add_model.html', {"form": form, "title": title, "creat_time": creat_time})


def user_edit01(request, nid):
    """ 修改用户 """
    row_object = models.User.objects.filter(id=nid).first()
    if request.method == 'GET':
        form = UserForm(instance=row_object)
        return render(request, 'user_edit01.html', {'form': form})
    form = UserForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/user/list01/')
    return render(request, 'user_list01.html', {"form": form})


def user_delete01(request):
    """ 删除员工 """
    uid = request.GET.get('uid')
    exists = models.User.objects.filter(id=uid).exists()
    if not exists:
        return JsonResponse({"status": False, 'error': "数据不存在,删除失败"})
    models.User.objects.filter(id=uid).delete()
    return JsonResponse({"status": True})


# -------------- 员工管理 end -------------- #


# -------------- 仓储管理 -------------- #
def mate_list01(request):
    """物料列表"""

    # --------------- 页码跳转框 ---------------
    data_dict = {}
    value = request.GET.get('page')
    if value:
        data_dict["name__contains"] = value  # contains:包含
    # queryset = models.Material.objects.filter(**data_dict).order_by("id")  # 获取所有包含“value”的数据2
    # --------------- 页码跳转框 end ---------------

    # --------------- 分页显示 ---------------
    if not request.GET.get('page', 1):
        return redirect('/index/home01/')
    page = int(request.GET.get('page', 1))  # 当前页
    page_size = 10
    start = (page - 1) * page_size
    end = page * page_size

    # --------------- 名称搜索框 ---------------
    data_dict = {}
    value_ch = request.GET.get('choice_name')
    if value_ch:
        data_dict["name__contains"] = value_ch
        queryset = models.Material.objects.filter(**data_dict).order_by("id")  # 获取所有包含“value”的数据2
    else:
        queryset = models.Material.objects.all().order_by("id")[start: end]
    form = MateForm()
    # --------------- 名称搜索框 end ---------------

    # 页码
    total_count = models.Material.objects.all().count()  # 获取数据的总数量
    total_page_count, div = divmod(total_count, page_size)  # 除法计算出页码总数， div：除法的商
    if div:
        total_page_count += 1

    # 计算当前页的前5页和后5页
    plus = 2
    if total_page_count <= 2 * plus:
        # 数据量比较少，没有达到11页时
        start_page = 1
        end_page = total_page_count
    else:
        # 数据量比较多，超出11页时，
        if page <= plus:
            # (小极值)
            start_page = 1
            end_page = 2 * plus + 1
        else:
            # （大极值）
            if (page + plus) > total_page_count:
                start_page = total_page_count - 2 * plus
                end_page = total_page_count
            else:
                start_page = page - plus
                end_page = page + plus

    # 页码
    page_str_list = []

    # 首页
    page_str_list.append('<li><a href="?page={}">首页</a></li>'.format(1))

    # 上一页
    if page > 1:
        prev = '<li><a href="?page={}">上一页</a></li>'.format(page - 1)
    else:
        prev = '<li><a href="?page={}">上一页</a></li>'.format(1)
    page_str_list.append(prev)

    # 页面
    for i in range(start_page, end_page + 1):  # 因为range为前取后不取，所以加1
        if i == page:
            ele = '<li class="active"><a href="?page={}">{}</a></li>'.format(i, i)
        else:
            ele = '<li><a href="?page={}">{}</a></li>'.format(i, i)

        page_str_list.append(ele)

    # 下一页
    if page < total_page_count:
        prev = '<li><a href="?page={}">下一页</a></li>'.format(page + 1)
    else:
        prev = '<li><a href="?page={}">下一页</a></li>'.format(total_page_count)
    page_str_list.append(prev)

    # 尾页
    page_str_list.append('<li><a href="?page={}">尾页</a></li>'.format(total_page_count))

    page_string = mark_safe("".join(page_str_list))  # 转成HTML代码，需导入mark_safe

    # ---------------分页显示 end ---------------

    return render(request, 'mate_list01.html',
                  {'form': form, 'queryset': queryset, 'page_string': page_string})


def mate_add01(request):
    title = '增加物料'
    if request.method == "GET":
        form = MateForm()
        return render(request, 'add_model.html', {"form": form, "title": title})
    # 校验数据是否合法：
    form = MateForm(data=request.POST)
    if form.is_valid():
        # 数据合法，ModelForm用简单的语句，将所有数据保存到数据库
        # form.instance.password = 123456
        form.save()
        return redirect('/mate/list01/')
    # 校验失败：
    return render(request, 'add_model.html', {"form": form, "title": title})


def mate_edit01(request, nid):
    row_object = models.Material.objects.filter(id=nid).first()
    if request.method == 'GET':
        form = MateEditForm(instance=row_object)
        return render(request, 'mate_edit01.html', {'form': form})
    form = MateEditForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/mate/list01/')
    return render(request, 'mate_edit01.html', {"form": form})


def mate_delete01(request):
    uid = request.GET.get('uid')
    exists = models.Material.objects.filter(id=uid).exists()
    if not exists:
        return JsonResponse({"status": False, 'error': "数据不存在,删除失败"})
    models.Material.objects.filter(id=uid).delete()
    return JsonResponse({"status": True})


# -------------- 仓储管理 end -------------- #


# -------------- 供应商管理 -------------- #
def supplier_list01(request):
    """供应商管理"""

    # --------------- 页码跳转框 ---------------
    data_dict = {}
    value = request.GET.get('page')
    if value:
        data_dict["name__contains"] = value  # contains:包含
    # queryset = models.Material.objects.filter(**data_dict).order_by("id")  # 获取所有包含“value”的数据2
    # --------------- 页码跳转框 end ---------------

    # --------------- 分页显示 ---------------
    if not request.GET.get('page', 1):
        return redirect('/index/home01/')
    page = int(request.GET.get('page', 1))  # 当前页
    page_size = 10
    start = (page - 1) * page_size
    end = page * page_size

    # --------------- 名称搜索框 ---------------
    data_dict = {}
    value_ch = request.GET.get('choice_name')
    if value_ch:
        data_dict["name__contains"] = value_ch
        queryset = models.Supplier.objects.filter(**data_dict).order_by("id")  # 获取所有包含“value”的数据2
    else:
        queryset = models.Supplier.objects.all().order_by("id")[start: end]
    form = SupplierForm()
    # --------------- 名称搜索框 end ---------------

    # 页码
    total_count = models.Supplier.objects.all().count()  # 获取数据的总数量
    total_page_count, div = divmod(total_count, page_size)  # 除法计算出页码总数， div：除法的商
    if div:
        total_page_count += 1

    # 计算当前页的前5页和后5页
    plus = 2
    if total_page_count <= 2 * plus:
        # 数据量比较少，没有达到11页时
        start_page = 1
        end_page = total_page_count
    else:
        # 数据量比较多，超出11页时，
        if page <= plus:
            # (小极值)
            start_page = 1
            end_page = 2 * plus + 1
        else:
            # （大极值）
            if (page + plus) > total_page_count:
                start_page = total_page_count - 2 * plus
                end_page = total_page_count
            else:
                start_page = page - plus
                end_page = page + plus

    # 页码
    page_str_list = []

    # 首页
    page_str_list.append('<li><a href="?page={}">首页</a></li>'.format(1))

    # 上一页
    if page > 1:
        prev = '<li><a href="?page={}">上一页</a></li>'.format(page - 1)
    else:
        prev = '<li><a href="?page={}">上一页</a></li>'.format(1)
    page_str_list.append(prev)

    # 页面
    for i in range(start_page, end_page + 1):  # 因为range为前取后不取，所以加1
        if i == page:
            ele = '<li class="active"><a href="?page={}">{}</a></li>'.format(i, i)
        else:
            ele = '<li><a href="?page={}">{}</a></li>'.format(i, i)

        page_str_list.append(ele)

    # 下一页
    if page < total_page_count:
        prev = '<li><a href="?page={}">下一页</a></li>'.format(page + 1)
    else:
        prev = '<li><a href="?page={}">下一页</a></li>'.format(total_page_count)
    page_str_list.append(prev)

    # 尾页
    page_str_list.append('<li><a href="?page={}">尾页</a></li>'.format(total_page_count))

    page_string = mark_safe("".join(page_str_list))  # 转成HTML代码，需导入mark_safe

    # ---------------分页显示 end ---------------

    return render(request, 'supplier_list01.html',
                  {'form': form, 'queryset': queryset, 'page_string': page_string})


def supplier_add01(request):
    title = '增加供应商'
    if request.method == "GET":
        form = SupplierForm()
        return render(request, 'add_model.html', {"form": form, "title": title})
    # 校验数据是否合法：
    form = SupplierForm(data=request.POST)
    if form.is_valid():
        # 数据合法，SupplierForm用简单的语句，将所有数据保存到数据库
        # form.instance.password = 123456
        form.save()
        return redirect('/supplier/list01/')
    # 校验失败：
    return render(request, 'add_model.html', {"form": form, "title": title})


def supplier_edit01(request, nid):
    row_object = models.Supplier.objects.filter(id=nid).first()
    if request.method == 'GET':
        form = SupplierEditForm(instance=row_object)
        return render(request, 'supplier_edit01.html', {'form': form})
    form = SupplierEditForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/supplier/list01/')
    return render(request, 'supplier_edit01.html', {"form": form})


def supplier_delete01(request):
    """删除供应商"""

    uid = request.GET.get('uid')
    print(uid)
    exists = models.Supplier.objects.filter(id=uid).exists()
    if not exists:
        return JsonResponse({"status": False, 'error': "数据不存在,删除失败"})
    models.Supplier.objects.filter(id=uid).delete()
    return JsonResponse({"status": True})


# -------------- 供应商管理 end -------------- #


# -------------- 入库单管理 -------------- #
def warehousing_list01(request):
    """入库单列表（展示一年的数据）"""

    # 追加虚拟数据：
    # for i in range(50):
    #     models.Warehousing.objects.create(name_id=52, supplier_id=3, quantity=1212.22,
    #                                       unit_price=13.12, price=22.11, unit='公斤', operator_id=1, approved=0
    #                                       )

    # --------------- 页码跳转框 ---------------
    data_dict = {}
    value = request.GET.get('page')
    if value:
        data_dict["warehousing_name__contains"] = value  # contains:包含

    # --------------- 页码跳转框 end ---------------

    # --------------- 分页显示 ---------------

    if not request.GET.get('page', 1):
        return redirect('/index/home01/')

    page = int(request.GET.get('page', 1))  # 当前页
    page_size = 10
    start = (page - 1) * page_size
    end = page * page_size

    # --------------- 名称搜索框【关联表的搜索案例】 ---------------
    data_dict = {}
    value_ch = request.GET.get('choice_name')
    today = dt.date.today()  # 获取当前日期
    oneyearago = today - datetime.timedelta(days=365)  # oneyearago 从现在算一年以前的日期
    if value_ch:
        data_dict["warehousing_name__name__contains"] = value_ch
        queryset = models.Warehousing.objects.filter(**data_dict).order_by(
            "approved", "-warehousing_date")  # 获取所有包含“value”的数据2
    else:
        queryset = models.Warehousing.objects.filter(warehousing_date__gte=oneyearago).order_by(
            "approved", "-warehousing_date")[start: end]  # 一年以内的数据
    form = WarehousingForm()
    # --------------- 名称搜索框 end ---------------

    # 页码
    total_count = models.Warehousing.objects.all().count()  # 获取数据的总数量
    total_page_count, div = divmod(total_count, page_size)  # 除法计算出页码总数， div：除法的商
    if div:
        total_page_count += 1

    # 计算当前页的前5页和后5页
    plus = 2
    if total_page_count <= 2 * plus:
        # 数据量比较少，没有达到11页时
        start_page = 1
        end_page = total_page_count
    else:
        # 数据量比较多，超出11页时，
        if page <= plus:
            # (小极值)
            start_page = 1
            end_page = 2 * plus + 1
        else:
            # （大极值）
            if (page + plus) > total_page_count:
                start_page = total_page_count - 2 * plus
                end_page = total_page_count
            else:
                start_page = page - plus
                end_page = page + plus

    # 页码
    page_str_list = []

    # 首页
    page_str_list.append('<li><a href="?page={}">首页</a></li>'.format(1))

    # 上一页
    if page > 1:
        prev = '<li><a href="?page={}">上一页</a></li>'.format(page - 1)
    else:
        prev = '<li><a href="?page={}">上一页</a></li>'.format(1)
    page_str_list.append(prev)

    # 页面
    for i in range(start_page, end_page + 1):  # 因为range为前取后不取，所以加1
        if i == page:
            ele = '<li class="active"><a href="?page={}">{}</a></li>'.format(i, i)
        else:
            ele = '<li><a href="?page={}">{}</a></li>'.format(i, i)

        page_str_list.append(ele)

    # 下一页
    if page < total_page_count:
        prev = '<li><a href="?page={}">下一页</a></li>'.format(page + 1)
    else:
        prev = '<li><a href="?page={}">下一页</a></li>'.format(total_page_count)
    page_str_list.append(prev)

    # 尾页
    page_str_list.append('<li><a href="?page={}">尾页</a></li>'.format(total_page_count))

    page_string = mark_safe("".join(page_str_list))  # 转成HTML代码，需导入mark_safe

    # ---------------分页显示 end ---------------

    return render(request, 'warehousing_list01.html',
                  {'form': form, 'queryset': queryset, 'page_string': page_string})


def warehousing_add01(request):
    """增加入库单"""
    global quantity  # 声明全局变量
    formAdd = WarehousingAddForm()
    form = WarehousingForm()

    queryset = models.Warehousing.objects.filter(approved=0).order_by('-warehousing_date')  # 未审核数据
    if request.method == "GET":
        queryset = models.Warehousing.objects.filter(approved=0).order_by('-warehousing_date')
        return render(request, 'warehousing_add01.html', {'form': form, 'formAdd': formAdd, 'queryset': queryset})
    # 校验数据是否合法：
    form = WarehousingAddForm(data=request.POST)

    if form.is_valid():
        # 计算单价
        data = form.cleaned_data
        # print(data)
        price = form.cleaned_data.get('price')
        quantity = form.cleaned_data.get('quantity')
        unit_price = price / quantity
        form.instance.unit_price = unit_price
        date = form.cleaned_data.get('warehousing_date')
        produceDate = form.cleaned_data.get('produceDate')
        if produceDate > date:
            messages.error(request, "生产日期不能大于入库日期！")
            return HttpResponseRedirect('/warehousing/add01/')
        name = form.cleaned_data.get('warehousing_name')

        # 判断该条入库单的日期以后是否有该物品的盘点记录，如果有则不得入库
        exists = models.Inventory.objects.filter(Q(name=name) & Q(inventoryDate__gt=date)).exists()
        if exists:
            messages.error(request, '该日期已完成盘点，盘点以前的日期禁止入库！')
            return HttpResponseRedirect('/warehousing/add01/')

        info_dict = request.session.get('info')  # 获取操作员信息
        form.instance.operator_id = (info_dict['id'])  # # 获取操作员ID

        # ------------------ 计算批次编码[ 类别号 + 物品ID + 当前时间 ]、截止日期 ------------------
        # todaytime = dt.date.today()  # 获取当前日期(2023-03-22)
        # tt_str = tt.strftime("%Y-%m-%d %H:%M:%S,%A,%B")   # 转换成字符串(2023-03-22 22:36:33,Wednesday,March)
        tt = datetime.datetime.now()  # 获取当前日期和时间(2023-03-22 22:13:10.725864)
        tt_str = tt.strftime("%Y%m%d%H%M%S")  # 转换成字符串(20230322223847)
        mid = models.Material.objects.filter(name=name).first().id
        category = models.Material.objects.filter(name=name).first().category
        batchCode = str(category) + str(mid) + tt_str  # 算得批次编码（1320230322230440）,len(batchCode) = 16
        guarantee_period = models.Material.objects.filter(name=name).first().guarantee_period  # 保质期
        produceDate = form.cleaned_data.get('produceDate')  # 获取生产日期
        closingDate = produceDate + datetime.timedelta(days=guarantee_period)  # 截止日期

        form.instance.approved = 0  # 将 0 赋值于"审核"字段
        form.instance.batchCode = batchCode  # 将 编码 赋值于"批次编码"字段
        form.instance.surplus = quantity  # 将 入库数量 赋值于"剩余数量"字段
        form.instance.closingDate = closingDate  # 将 截止日期 赋值于"截止日期"字段

        # ------------------ 计算批次编码 end------------------

        # 数据合法，SupplierForm用简单的语句，将所有数据保存到数据库
        exists = models.User.objects.filter(id=info_dict['id']).exists()
        if not exists:
            messages.error(request, '请使用员工入口进入，再做操作')
            return HttpResponseRedirect('/index/home01/')
        form.save()
        return redirect('/warehousing/add01/')
    # 校验失败：
    return render(request, 'warehousing_add01.html', {'form': form, 'formAdd': formAdd, 'queryset': queryset})


def warehousing_list_approved01(request, nid):
    """入库单列表中的审核功能"""
    # 判断该条入库单的日期以后是否有该物品的盘点记录，如果有则不得审核
    date = models.Warehousing.objects.filter(id=nid).first().warehousing_date
    name = models.Warehousing.objects.filter(id=nid).first().warehousing_name
    exists = models.Inventory.objects.filter(Q(name=name) & Q(inventoryDate__gt=date)).exists()
    if not exists:
        models.Warehousing.objects.filter(id=nid).update(approved=1)
        return redirect('/warehousing/list01/')
    messages.error(request, '该日期盘点已完成，盘点以前的数据不得入库！')
    return HttpResponseRedirect('/warehousing/list01/')
    # return redirect('/warehousing/list01/')


def warehousing_add_approved01(request, nid):
    """增加入库单中的审核功能"""
    # 判断该条入库单的日期以后是否有该物品的盘点记录，如果有则不得审核
    date = models.Warehousing.objects.filter(id=nid).first().warehousing_date
    name = models.Warehousing.objects.filter(id=nid).first().warehousing_name
    exists = models.Inventory.objects.filter(Q(name=name) & Q(inventoryDate__gt=date)).exists()
    if not exists:
        models.Warehousing.objects.filter(id=nid).update(approved=1)
        return redirect('/warehousing/add01/')
    messages.error(request, '该日期盘点已完成，盘点以前的数据不得入库！')
    return HttpResponseRedirect('/warehousing/add01/')


def warehousing_list_delete01(request):
    """ 入库单列表中的删除功能 """
    uid = request.GET.get('uid')
    exists = models.Warehousing.objects.filter(id=uid).exists()
    if not exists:
        return JsonResponse({"status": False, 'error': "数据不存在,删除失败"})

    models.Warehousing.objects.filter(id=uid).delete()
    return JsonResponse({"status": True})


def warehousing_add_delete01(request, nid):
    """新增入库单中的删除功能"""
    models.Warehousing.objects.filter(id=nid).delete()
    return redirect('/warehousing/add01/')


def warehousing_list_edit01(request, nid):
    """入库单列表中的修改功能"""
    row_object = models.Warehousing.objects.filter(id=nid).first()
    if request.method == 'GET':
        form = WarehousingAddForm(instance=row_object)
        return render(request, 'warehousing_edit01.html', {'form': form})
    form = WarehousingAddForm(data=request.POST, instance=row_object)
    if form.is_valid():
        price = form.cleaned_data.get('price')
        quantity = form.cleaned_data.get('quantity')
        unit_price = price / quantity
        form.instance.unit_price = unit_price
        date = form.cleaned_data.get('warehousing_date')
        name = form.cleaned_data.get('warehousing_name')

        # 判断该条入库单的日期以后是否有该物品的盘点记录，如果有则不得入库
        exists = models.Inventory.objects.filter(Q(name=name) & Q(inventoryDate__gte=date)).exists()
        if exists:
            messages.error(request, '该日期已完成盘点，盘点以前的数据不得入库！')
            return HttpResponseRedirect('/warehousing/add01/')

        info_dict = request.session.get('info')  # 获取操作员信息
        form.instance.operator_id = (info_dict['id'])  # 获取操作员ID
        exists = models.User.objects.filter(id=info_dict['id']).exists()
        if not exists:
            return HttpResponse('请使用员工入口进入，再做操作')
        form.save()
        return redirect('/warehousing/list01/')
    return render(request, 'warehousing_edit01.html', {"form": form})


@csrf_exempt
def warehousing_print(request):
    """ 打印入库单 AJax请求
    1、后端查询数据后，把queryset数据，经过list，转成列表
    2、遍历列表处理数据，
    3、发送到前端数据
    4、前端把数据增加到窗口列表
    """
    data = request.POST
    date = data.get('warehousing_date')
    supplier = data.get('supplier')

    if supplier:
        printobject = models.Warehousing.objects.filter(
            Q(warehousing_date=date) & Q(supplier=supplier)).values()
        if printobject:
            printlist = list(printobject)  # 把Queryset转成列表
            for dict in printlist:  # 遍历列表中的字典，新增并删除无用数据
                id = dict['warehousing_name_id']  # 提取字典中KEY对应的值
                batchCode = dict['batchCode']  # 提取字典中KEY对应的值
                name = models.Material.objects.filter(id=id).first().name  # 获取物料名称
                unit = models.Material.objects.filter(id=id).first().unit  # 获取计量单位
                dict['name'] = name  # 给字典赋值一个新的数据：
                dict['unit'] = unit  # 给字典赋值一个新的数据：
                dict['batchCode'] = batchCode  # 给字典赋值一个新的数据：

                del dict['warehousing_date']  # 删除字典中的一项
                del dict['supplier_id']  # 删除字典中的一项
                del dict['operator_id']  # 删除字典中的一项
                del dict['warehousing_name_id']  # 删除字典中的一项
                del dict['approved']  # 删除字典中的一项

            return JsonResponse({"status": True, "PRINT_QUERYSET": list(printobject)})
        else:
            error_text = '没有入库数据。请重新录入'
            return JsonResponse({"status": False, 'tips': error_text})
    error_text = '没有入库数据。请重新录入'
    return JsonResponse({"status": False, 'tips': error_text})


def warehousing_print_bm(request):
    global batchCode
    data = request.GET
    if not data:
        return redirect('/warehousing/list01/')
    batchCode = list(data)[0]
    exists = models.Warehousing.objects.filter(batchCode=batchCode).exists()
    if exists:
        file_path = r'app01/ExcelFiles/batchCode.xlsx'
        exists = os.path.exists(file_path)
        if exists:
            warehousing_name = str(models.Warehousing.objects.filter(batchCode=batchCode).first().warehousing_name)
            supplier = str(models.Warehousing.objects.filter(batchCode=batchCode).first().supplier)
            warehousing_date = models.Warehousing.objects.filter(batchCode=batchCode).first().warehousing_date
            quantity = models.Warehousing.objects.filter(batchCode=batchCode).first().quantity
            produceDate = models.Warehousing.objects.filter(batchCode=batchCode).first().produceDate
            closingDate = models.Warehousing.objects.filter(batchCode=batchCode).first().closingDate

            wb = load_workbook(r'app01/ExcelFiles/batchCode.xlsx')
            sheet = wb.worksheets[0]

            sheet['B1'] = batchCode
            sheet['B2'] = warehousing_name
            sheet['B3'] = supplier
            sheet['B4'] = quantity
            sheet['B5'] = warehousing_date
            sheet['B6'] = produceDate
            sheet['B7'] = closingDate

            sheet['E1'] = batchCode
            sheet['E2'] = warehousing_name
            sheet['E3'] = supplier
            sheet['E4'] = quantity
            sheet['E5'] = warehousing_date
            sheet['E6'] = produceDate
            sheet['E7'] = closingDate

            wb.save(r'app01/ExcelFiles/batchCode1.xlsx')
        else:
            print('源文件不存在')

        # 文件下载
        file_path = r"app01/ExcelFiles/batchCode1.xlsx"
        try:
            file = open(file_path, 'rb')
            ret = FileResponse(file, as_attachment=True, filename="批次_" + batchCode + ".xlsx")
            return ret
        except Exception:
            raise Http404("Download error")
