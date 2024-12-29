"""
本视图函数包括：
1、盘点单元
2、出库单元
"""
import decimal
import datetime
import datetime as dt
# from datetime import date

from app01 import models
from django import forms
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt

from app01.utils.bootstrap import BootStrapModelForm


class InventoryForm(BootStrapModelForm):
    class Meta:
        model = models.Inventory
        fields = '__all__'
        # exclude = ["password"]


class InventoryAddForm(BootStrapModelForm):
    class Meta:
        model = models.Inventory
        fields = ['name', 'inventoryQuantity', 'bookAmount']
        widgets = {
            "name": forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true",
                       "data-size": "10", "data-header": "搜索关键字："})
        }


class OutboundForm(BootStrapModelForm):
    class Meta:
        model = models.outbound
        fields = '__all__'
        widgets = {
            "name": forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true",
                       "data-size": "10", "data-header": "搜索关键字："}),

            "department": forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true",
                       "data-size": "10", "data-header": "搜索关键字："})
        }


class OutboundAddForm(BootStrapModelForm):
    class Meta:
        model = models.outbound
        fields = ['date', 'name', 'department', 'outbound']
        widgets = {
            "name": forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true",
                       "data-size": "10", "data-header": "搜索关键字："})
        }


def inventory_list01(request):
    """ 盘点数据列表（只显示最近两次盘点的数据） """
    # --------------- 获取并定义最近两次盘点的时间段,页面只显示最近两次盘点的数据 ---------------
    global date_rang
    now_date = dt.date.today()
    final_date = now_date
    last_date = now_date

    date_rang = ()

    exists = models.Inventory.objects.all().exists()
    if exists:  # 盘点表有数据
        # final_date：上次盘点日期
        final_date = models.Inventory.objects.all().order_by('inventoryDate').last().inventoryDate
        exists = models.Inventory.objects.all().exclude(inventoryDate=final_date).exists()
        # last_date：上一次的上一次盘点日期
        if exists:  # 排除上一次盘点日期数据，盘点表还有数据
            last_date = models.Inventory.objects.all().exclude(inventoryDate=final_date).order_by(
                'inventoryDate').last().inventoryDate
        else:  # 排除上一次盘点日期数据，盘点表没有数据
            last_date = final_date

    exists = models.Inventory.objects.all().filter(inventoryDate__lt=last_date).exists()
    if exists:
        start_date = models.Inventory.objects.all().filter(inventoryDate__lt=last_date).order_by(
            'inventoryDate').last().inventoryDate
    else:
        start_date = last_date

    date_rang = (start_date, final_date)
    # if start_date:
    #     date_rang = (start_date, final_date)
    # else:
    #     if last_date:
    #         date_rang = (last_date, final_date)
    #     else:
    #         if start_date:
    #             date_rang = (final_date, final_date)
    #         else:
    #             return redirect('/index/home01/')

    # --------------- 页码跳转框 ---------------
    data_dict = {}
    value = request.GET.get('page')
    if value:
        data_dict["name__contains"] = value  # contains:包含
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
    if value_ch:
        data_dict["name__name__contains"] = value_ch
        queryset = models.Inventory.objects.filter(**data_dict).order_by(
            "-inventoryDate")  # 获取所有包含“value”的数据2
    else:
        queryset = models.Inventory.objects.filter(Q(inventoryDate__range=date_rang)).order_by("-inventoryDate")[
                   start: end]
    form = InventoryForm()
    # --------------- 名称搜索框 end ---------------

    # 页码
    total_count = models.Inventory.objects.filter(Q(inventoryDate__range=date_rang)).count()  # 获取数据的总数量
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

    return render(request, 'inventory_list01.html',
                  {'form': form, 'queryset': queryset, 'page_string': page_string})


@csrf_exempt
def inventory_add01(request):
    """ 录入盘点数据 """

    if "js_date_str" in vars().keys():
        # print('yes')
        return redirect('/inventory/list01/')
    # print('no')

    title = '录入盘点数据'
    list_title = '盘点数据列表（未审核）'

    # 获取 Ajax 发来的用户选择日期,并且转化成 datetime.date 类型
    fmt = '%Y-%m-%d'
    js_date_str_tt = datetime.datetime.strptime(js_date_str, fmt)
    js_date = datetime.datetime.date(js_date_str_tt)  # 用户录入的盘点日期

    # now_date = dt.date.today()  # 获取当前日期
    yesterday_js_date = js_date - datetime.timedelta(days=1)  # 获取入库单截止日日期:盘点日期前一天
    info_dict = request.session.get('info')  # 获取当前操作员信息
    operator = (info_dict['id'])  # # 获取操作员ID
    username = (info_dict['name'])  # # 获取操作员姓名

    # 如果登陆者是管理员，无权操作，返回主页面
    exists = models.User.objects.filter(name=username).exists()
    if not exists:
        return redirect('/index/home01/')

    queryset = models.Inventory.objects.filter(approved=0).order_by('-inventoryDate')
    formAdd = InventoryAddForm()
    form = InventoryForm()

    if request.method == "GET":
        return render(request, 'inventory_add01.html',
                      {'form': form, 'formAdd': formAdd, 'queryset': queryset, 'title': title,
                       'list_title': list_title})

    # 获取前端提交的数据
    formAdd = InventoryAddForm(data=request.POST)
    data = request.POST
    name_id = data.get('name')  # 获取用户输入的物料名称的ID
    name = models.Material.objects.get(id=name_id)  # 获取用户输入的物料名称
    inventoryQuantity = decimal.Decimal(data.get('inventoryQuantity'))  # 获取用户输入的盘点值(str),并转化成decimal类型
    bookAmount = data.get('bookAmount')  # 获取用户输入的账面金额
    form = InventoryForm()

    # 校验一：如果有过盘点，不能录入金库存额数据
    exists = models.Inventory.objects.filter(name_id=name_id).exists()
    if exists and bookAmount:
        formAdd.add_error = "再次盘点该物品，不能录入金额"
        return render(request, 'inventory_add01.html',
                      {'form': form, 'formAdd': formAdd, 'queryset': queryset, 'title': title,
                       'list_title': list_title})

    # 校验二：如果找到该日期或该日期以后的时间内，有该物品有盘点数据，则返回提示使用修改按钮修改数据
    exists = models.Inventory.objects.filter(Q(name_id=name_id) & Q(
        inventoryDate__gte=js_date)).exists()
    if exists:
        formAdd = InventoryAddForm()
        formAdd.add_error = js_date_str + "---这个时间该物品已有盘点数据"
        queryset = models.Inventory.objects.filter(Q(name_id=name_id) & Q(
            inventoryDate=js_date))
        return render(request, 'inventory_add01.html',
                      {'form': form, 'formAdd': formAdd, 'queryset': queryset, 'title': title,
                       'list_title': list_title})

    formAdd.add_error = ''
    if formAdd.is_valid():
        exists = models.Inventory.objects.filter(Q(name_id=name_id) & Q(
            inventoryDate__lt=js_date)).exists()
        if exists:  # 如果盘点日期以前有该物品数据，说明不是首次录入该物料
            # print('--------------------------------------------')
            last_date = models.Inventory.objects.filter(Q(name_id=name_id) & Q(
                inventoryDate__lt=js_date)).last().inventoryDate
            # print('上次盘点日期：', last_date)
            # print('入库截止日期：', yesterday_js_date)
            # print('今天日期：', now_date)
            # print('--------------------------------------------')
            # print('录入的盘点数量：', inventoryQuantity)

            # ----------- 上次盘点数量 -----------
            last_book_quantity = models.Inventory.objects.filter(Q(name_id=name_id) & Q(
                inventoryDate__lt=js_date)).last().inventoryQuantity
            # print("上次盘点数量:", last_book_quantity)

            # ----------- 上次库存金额 -----------
            last_book_amount = models.Inventory.objects.filter(Q(name_id=name_id) & Q(
                inventoryDate__lt=js_date)).last().bookAmount
            # print("上次库存金额:", last_book_amount)

            # ----------- 计算本期入库数量[包含所取时间] （该物品 & 上次盘点时间到今天时间段 & 进货量的总和）-----------
            # 计算本期入库合计数量 Q语法计算
            sum_quantity_dict = models.Warehousing.objects.filter(
                Q(warehousing_name=name) & Q(warehousing_date__range=(last_date, yesterday_js_date)) & Q(
                    approved=1)).aggregate(
                a=Sum('quantity'))
            if sum_quantity_dict['a']:
                sum_quantity = sum_quantity_dict['a']
            else:
                sum_quantity = 0
            # print('本期入库数量：', sum_quantity)

            # ----------- 计算本期入库金额 -----------
            sum_price_dict = models.Warehousing.objects.filter(
                Q(warehousing_name=name) & Q(warehousing_date__range=(last_date, yesterday_js_date)) & Q(
                    approved=1)).aggregate(
                a=Sum('price'))
            if sum_price_dict['a']:
                sum_price = sum_price_dict['a']
            else:
                sum_price = 0
            # print('本期入库金额：', sum_price)

            # ----------- 计算本期出库数量 -----------
            sum_outbound_dict = models.outbound.objects.filter(
                Q(name=name) & Q(date__range=(last_date, yesterday_js_date)) & Q(
                    approved=1)).aggregate(
                a=Sum('outbound'))
            if sum_outbound_dict['a']:
                sum_outbound = sum_outbound_dict['a']
            else:
                sum_outbound = 0
            # print('本期出库数量：', sum_outbound)

            # ----------- 计算本期出库金额 -----------
            sum_issue_amount_dict = models.outbound.objects.filter(
                Q(name=name) & Q(date__range=(last_date, yesterday_js_date)) & Q(
                    approved=1)).aggregate(
                a=Sum('issueAmount'))
            if sum_issue_amount_dict['a']:
                sum_issue_amount = sum_issue_amount_dict['a']
            else:
                sum_issue_amount = 0
            # print('本期出库金额：', sum_issue_amount)

            # ----------- 计算：账面应有数量 = 上次盘点数量 + 本期入库数量 - 本期出库数量 -----------
            now_book_quantity = last_book_quantity + sum_quantity - sum_outbound
            # print('账面应有数量：', now_book_quantity)

            # ----------- 计算：账面应有金额 = 期初金额 + 本期入库金额 - 本期出库金额 -----------
            now_book_amount = last_book_amount + sum_price - sum_issue_amount
            # print('账面应有金额：', now_book_amount)

            # ----------- 计算：账面库存单价 = 账面应有金额 / 账面应有数量 -----------
            now_unit_price = now_book_amount / now_book_quantity
            # print('本期库存单价：', now_unit_price)

            # ----------- 计算本期库存金额=(本次盘点数量 * 本期库存单价) -----------
            now_amount = inventoryQuantity * now_unit_price
            # print('本期库存金额:', now_amount)

            # ----------- 计算：误差数量 = 盘点数量 - 账面应有数量 -----------
            errorsNumber = inventoryQuantity - now_book_quantity
            # print('误差数量：', errorsNumber)

            # ----------- 计算：误差金额 = 盘点数量 * 账面库存单价 - 账面应有金额 -----------
            errorsAmount = inventoryQuantity * now_unit_price - now_book_amount
            # print('误差金额：', errorsAmount)
            # print('--------------------------------------------')

            # 把每个字段的值 赋值于对应字段
            formAdd.instance.inventoryDate = js_date
            formAdd.instance.name_id = name_id
            formAdd.instance.inventoryQuantity = inventoryQuantity
            formAdd.instance.bookQuantity = now_book_quantity
            formAdd.instance.bookAmount = now_amount
            formAdd.instance.errorsNumber = errorsNumber
            formAdd.instance.errorsAmount = errorsAmount
            formAdd.instance.operator_id = operator
            formAdd.instance.approved = 0

            formAdd.save()
            return redirect('/inventory/add01/')
        else:  # 首次录入
            # 账面数量 = 盘点数量
            bookQuantity = inventoryQuantity
            errorsNumber = 0
            errorsAmount = 0

            # 把每个字段的值 赋值于对应字段
            formAdd.instance.inventoryDate = js_date
            formAdd.instance.name_id = name_id
            formAdd.instance.inventoryQuantity = inventoryQuantity
            formAdd.instance.bookQuantity = bookQuantity
            formAdd.instance.bookAmount = bookAmount
            formAdd.instance.errorsNumber = errorsNumber
            formAdd.instance.errorsAmount = errorsAmount
            formAdd.instance.operator_id = operator
            formAdd.instance.approved = 0

            formAdd.save()
        return redirect('/inventory/add01/')

    return render(request, 'inventory_add01.html',
                  {'form': form, 'formAdd': formAdd, 'queryset': queryset, 'title': title, 'list_title': list_title})


def inventory_edit01(request, nid):
    """ 编辑盘点表 """
    title = '编辑盘点数据'
    row_object = models.Inventory.objects.filter(id=nid).first()
    now_date = row_object.inventoryDate
    queryset = models.Inventory.objects.filter(inventoryDate=now_date)
    if not row_object:
        return redirect('/inventory/add01/')
    if request.method == 'GET':
        formAdd = InventoryAddForm(instance=row_object)
        form = InventoryForm()
        return render(request, 'inventory_add01.html',
                      {'form': form, 'formAdd': formAdd, 'queryset': queryset, 'title': title})
    formAdd = InventoryAddForm(data=request.POST, instance=row_object)

    # 获取提交来的名称、数量
    data = request.POST

    # 获取数据库这一行的其他数据，依据提交来的数量，计算其他数据
    inventoryQuantity = decimal.Decimal(data.get('inventoryQuantity'))  # 修改后盘点数量
    unit_price = row_object.bookAmount / row_object.inventoryQuantity  # 未修改时单价
    now_amount = unit_price * inventoryQuantity  # 修改后库存金额

    # print('未修改时库存金额:', row_object.bookAmount)
    # print('未修改时盘点数量:', row_object.inventoryQuantity)
    # print('未修改时单价:', unit_price)
    # print('未修后库存金额:', now_amount)

    errorsNumber = inventoryQuantity - row_object.bookQuantity  # 误差数量
    errorsAmount = unit_price * errorsNumber  # 误差金额

    formAdd.instance.inventoryQuantity = inventoryQuantity  # 修改后的盘点数量
    formAdd.instance.bookAmount = now_amount  # 库存金额
    formAdd.instance.errorsNumber = errorsNumber  # 误差数量
    formAdd.instance.errorsAmount = errorsAmount  # 误差金额

    if formAdd.is_valid():
        formAdd.save()
        models.Inventory.objects.filter(id=nid).update(bookAmount=now_amount)
        return redirect('/inventory/add01/')
    return render(request, 'inventory_add01.html',
                  {'form': formAdd, 'formAdd': formAdd, 'queryset': queryset, 'title': title})


def inventory_delete01(request):
    """ 删除盘点 """
    uid = request.GET.get('uid')
    exists = models.Inventory.objects.filter(id=uid).exists()
    if not exists:  # 判断数据是否存在
        return JsonResponse({"status": False, 'error': "数据不存在,删除失败"})
    models.Inventory.objects.filter(id=uid).delete()
    return JsonResponse({"status": True})


def inventory_list_approved01(request, nid):
    """出库单列表中的审核功能"""
    # uid = request.GET.get('uid')
    # exists = models.Inventory.objects.filter(id=uid).exists()
    # if not exists:
    #     return JsonResponse({"status": False, 'error': "数据不存在"})
    models.Inventory.objects.filter(id=nid).update(approved=1)
    return redirect('/inventory/list01/')


def inventory_add_approved01(request, nid):
    """出库单列表中的审核功能"""
    # uid = request.GET.get('uid')
    # exists = models.Inventory.objects.filter(id=uid).exists()
    # if not exists:
    #     return JsonResponse({"status": False, 'error': "数据不存在"})
    models.Inventory.objects.filter(id=nid).update(approved=1)
    return redirect('/inventory/add01/')


@csrf_exempt
def inventory_js_add01(request):
    """ Ajax 选择盘点日期 """
    global js_date_str
    js_date_str = ''
    data = request.GET
    js_date_str = data.get('js_date')
    return JsonResponse({"status": True})


@csrf_exempt
def inventory_hidden01(request):
    """ 隐藏/显示 账面金额输入框 """

    data = request.POST  # 获取由 Ajax 传来的全部值
    data_obj_name = data.get('name')  # 获取由 Ajax 传来的 name 的值

    if data_obj_name == '':
        return JsonResponse({"status": False})
    obj = models.Inventory.objects.filter(name=data_obj_name).first()
    if obj:
        hidden = True
    else:
        hidden = False
    return JsonResponse({"status": True, "value": hidden})


def outbound_list01(request):
    """ 出库单列表 从现在算一年以内的数据 """

    # --------------- 页码跳转框 ---------------
    data_dict = {}
    value = request.GET.get('page')
    if value:
        data_dict["name__contains"] = value  # contains:包含
    # --------------- 页码跳转框 end ---------------

    # --------------- 分页显示 ---------------
    page = int(request.GET.get('page', 1))  # 当前页
    page_size = 10
    start = (page - 1) * page_size
    end = page * page_size

    # --------------- 名称搜索框【关联表的搜索案例】 ---------------
    data_dict = {}
    value_ch = request.GET.get('choice_name')
    today = dt.date.today()  # 获取当前日期
    oneyearago = today - datetime.timedelta(days=365)  # oneyearago 从现在算一年以内的数据
    if value_ch:
        data_dict["name__name__contains"] = value_ch
        queryset = models.outbound.objects.filter(**data_dict).order_by("approved", "-date")  # 获取所有包含“value”的数据2
        # queryset = models.outbound.objects.filter(**data_dict).order_by("approved", "-date")  # 获取所有包含“value”的数据2
    else:
        queryset = models.outbound.objects.filter(date__gte=oneyearago).order_by("approved", "-date")[
                   # queryset = models.outbound.objects.filter(date__gte=oneyearago).order_by("approved", "-date")[
                   start: end]  # 一年以内的数据
    # --------------- 名称搜索框 end ---------------

    # --------------- 给页码规定form，前端显示出页码 ---------------
    form = OutboundForm()
    # --------------- 给页码规定form，前端显示出页码 end ---------------

    # 页码

    total_count = models.outbound.objects.all().count()  # 获取数据的总数量
    # total_count = models.outbound.objects.filter(Q(inventoryDate__range=date_rang)).count()  # 获取数据的总数量
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
    # 在 return 中传到前端
    page_string = mark_safe("".join(page_str_list))  # 转成HTML代码，需导入mark_safe

    # ---------------分页显示 end ---------------
    return render(request, 'outbound_list01.html', {
        'form': form, 'queryset': queryset, 'page_string': page_string
    })


@csrf_exempt
def outbound_js_list01(request):
    """ 出库单录入 (Ajax请求) """
    # --------------- 接收到Ajax请求，进行计算 ---------------
    form = OutboundAddForm(data=request.POST)
    if form.is_valid():
        name = form.cleaned_data.get('name')
        name_id = models.Material.objects.filter(name=name).first().id
        department = form.cleaned_data.get('department')
        info_dict = request.session.get('info')  # 获取当前操作员信息
        operator = (info_dict['id'])  # # 获取操作员ID
        # username = (info_dict['name'])   # 获取操作员姓名

        # 校验是否选择了名称和部门
        if name and department:
            # ---------- 获取出库时间，找到早于出库时间的上次盘点时间， ----------
            out_date = form.cleaned_data.get('date')

            # 判断出库日期以后是进行过盘点，如果有则不得出库
            exists = models.Inventory.objects.filter(Q(name=name) & Q(
                inventoryDate__gt=out_date)).exists()
            if exists:
                return JsonResponse({"status": False, 'tips': "该日期已经盘点完毕，此日期不得出库！"})

            # 判断是否有过盘点？是否有过入库？
            exists_pandian = models.Inventory.objects.filter(Q(name=name) & Q(
                inventoryDate__lt=out_date)).exists()
            if exists_pandian:  # 如果盘点过，
                pandian_date = models.Inventory.objects.filter(Q(name=name) & Q(
                    inventoryDate__lt=out_date)).last().inventoryDate
            else:
                exists_ruku = models.Warehousing.objects.filter(Q(warehousing_name=name) & Q(
                    warehousing_date__lte=out_date)).exists()
                if exists_ruku:  # 如果盘点过，但是有入库数据，
                    pandian_date = models.Warehousing.objects.filter(warehousing_name=name).first().warehousing_date
                else:  # 如果没有盘点过，也没有入库数据，
                    return JsonResponse({"status": False, 'tips': "没有库存数量，请重新录入"})

            # print('出库日期：', out_date, type(out_date))
            # print('上次盘点日期：', pandian_date, type(pandian_date))

            # ---------- 用户录入的出库数量 ----------
            outbound = form.cleaned_data.get('outbound')
            # print('出库数量：', outbound, type(outbound))

            # ---------- 盘点表账面金额 & 盘点数量 ----------
            if exists_pandian:  # 如果盘点过
                bookAmount = models.Inventory.objects.filter(Q(name=name) & Q(
                    inventoryDate__lt=out_date)).last().bookAmount
                inventoryQuantity = models.Inventory.objects.filter(Q(name=name) & Q(
                    inventoryDate__lt=out_date)).last().inventoryQuantity
            else:
                bookAmount = 0
                inventoryQuantity = 0
            # print('账面金额:', bookAmount, type(bookAmount))
            # print('盘点数量:', inventoryQuantity, type(inventoryQuantity))

            # ---------- 本期入库数量 ----------
            sum_quantity_dict = models.Warehousing.objects.filter(
                Q(warehousing_name=name) & Q(warehousing_date__range=(pandian_date, out_date)) & Q(
                    approved=1)).aggregate(
                a=Sum('quantity'))
            if sum_quantity_dict['a']:
                sum_quantity = sum_quantity_dict['a']
            else:
                sum_quantity = 0
            # print('本期入库数量：', sum_quantity, type(sum_quantity))

            # ---------- 本期入库金额（未审核的入库单将不计入入库） ----------
            sum_price_dict = models.Warehousing.objects.filter(
                Q(warehousing_name=name) & Q(warehousing_date__range=(pandian_date, out_date)) & Q(
                    approved=1)).aggregate(
                a=Sum('price'))
            if sum_price_dict['a']:
                sum_price = sum_price_dict['a']
            else:
                sum_price = 0
            # print('本期入库金额：', sum_price, type(sum_price))

            # ---------- 本期出库数量（未审核的出库单将计入出库） ----------
            sum_outbound_dict = models.outbound.objects.filter(
                Q(name=name) & Q(date__range=(pandian_date, out_date))).aggregate(aa=Sum('outbound'))
            if sum_outbound_dict['aa']:
                sum_outbound = sum_outbound_dict['aa']
            else:
                sum_outbound = 0
            # print('本期出库数量：', sum_outbound, type(sum_outbound))

            # ---------- 校验出库数量是否小于库存数量，小于库存数则继续计算 ----------
            # 库存数量 = 上次盘点数量 + 本期入库合计数量 - 本期出库数量
            all_quantity = sum_quantity + inventoryQuantity - sum_outbound
            if outbound > all_quantity:
                error_text = '库存数量为：' + str(all_quantity) + '，出库数量不足。请重新录入'
                return JsonResponse({"status": False, 'tips': error_text})

            all_price = bookAmount + sum_price  # 上次盘点账面金额+本期入库合计金额
            all_quantity = sum_quantity + inventoryQuantity  # 合计入库数量 = 上次盘点数量 + 本期入库合计数量
            # print('合计入库金额：', all_price, type(all_price))
            # print('合计入库数量：', all_quantity, type(all_quantity))
            out_unit_price = all_price / all_quantity  # 出库单价
            # print('出库单价：', out_unit_price, type(out_unit_price))
            # issueAmount = outbound * out_unit_price  # 出库金额

            # ---------- 按批次依次出库 ----------
            sum_outbound = 0  # 合计出库量
            cha_outbound = outbound  # 相差出库量
            while sum_outbound != outbound:
                table = models.Warehousing.objects.filter(Q(warehousing_name=name) & Q(surplus__gt=0) & Q(
                    approved=1)).order_by('closingDate').first()
                batchCode = table.batchCode  # 获取批次编码
                # print(batchCode)

                surplus = table.surplus  # surplus,报废期最近的批次库存量
                if surplus >= cha_outbound:  # 如果批次库存满足相差出库量
                    sum_outbound = sum_outbound + cha_outbound  # 累计出库数
                    models.Warehousing.objects.filter(batchCode=batchCode).update(
                        surplus=surplus - cha_outbound)  # 更新入库表批次库存量

                    # ---------- 储存出库单数据 (使用create()方法) ----------
                    models.outbound.objects.create(
                        date=out_date,
                        outbound=cha_outbound,
                        issueUnitPrice=out_unit_price,
                        issueAmount=cha_outbound * out_unit_price,
                        department=department,
                        name_id=name_id,
                        operator_id=operator,
                        approved=0,
                        batchCode=batchCode
                    )
                    # ---------- 储存出库单数据 end ----------
                else:
                    sum_outbound = sum_outbound + surplus
                    cha_outbound = outbound - sum_outbound
                    models.Warehousing.objects.filter(batchCode=batchCode).update(
                        surplus=0)  # 更新入库表批次库存量

                    models.outbound.objects.create(
                        date=out_date,
                        outbound=surplus,
                        issueUnitPrice=out_unit_price,
                        issueAmount=surplus * out_unit_price,
                        department=department,
                        name_id=name_id,
                        operator_id=operator,
                        approved=0,
                        batchCode=batchCode
                    )
                if sum_outbound == outbound:
                    break
            # ---------- 按批次出库 end ----------
            return JsonResponse({"status": True})

    return JsonResponse({"status": False, 'error': form.errors})


def outbound_list_approved01(request, nid):
    """出库单列表中的审核功能"""
    # uid = request.GET.get('uid')
    # exists = models.outbound.objects.filter(id=uid).exists()
    # if not exists:
    #     return JsonResponse({"status": False, 'error': "数据不存在"})
    models.outbound.objects.filter(id=nid).update(approved=1)
    return redirect('/outbound/list01/')


def outbound_list_delete01(request):
    """ 出库单列表中的删除功能 """
    uid = request.GET.get('uid')
    exists = models.outbound.objects.filter(id=uid).exists()
    if not exists:
        return JsonResponse({"status": False, 'error': "数据不存在,删除失败"})
    models.outbound.objects.filter(id=uid).delete()
    return JsonResponse({"status": True})


def outbound_window_edit01(request):
    """ 返回修改出库单的弹窗数据

        # 方式一：获取 row_object 中的值，并构造一个字典套字典返还前端：
        row_object = models.outbound.objects.filter(id=uid).first()  # 获取当前行数据，row_object是一个对象
        result  = {
            "status":True,
            "data": {
                "date": row_object.date,
                "department": row_object.department,
                "name": row_object.name,
                "outbound": row_object.outbound,
                }
        }
    return JsonResponse(result)
    """

    uid = request.GET.get("uid")
    # 方式二：直接从queryset对象获取相关数据，就是一个字典，返回前端。更简洁方便。
    orw_dict = models.outbound.objects.filter(id=uid).values(
        'date', 'department', 'name', 'outbound').first()  # 获取当前行某些列的数据，orw_dict是一个字典
    # print(orw_dict)
    # {'date': datetime.date(2023, 3, 11), 'department': 1, 'name': 2, 'outbound': Decimal('12.03')}
    if not orw_dict:
        return JsonResponse({"status": False, 'error': "数据不存在"})
    result = {
        "status": True,
        "data": orw_dict
    }
    return JsonResponse(result)


@csrf_exempt
def outbound_list_edit01(request):
    """ 修改出库单 """
    uid = request.GET.get("uid")
    orw_object = models.outbound.objects.filter(id=uid).first()
    data = request.POST
    if not orw_object:
        return JsonResponse({"status": False, 'tips': "数据不存在"})
    form = OutboundAddForm(data=request.POST, instance=orw_object)
    if form.is_valid():

        outbound = form.cleaned_data.get('outbound')  # 获取Alax发来的 出库数量
        out_date = form.cleaned_data.get('date')  # 获取Alax发来的 出库日期
        name = form.cleaned_data.get('name')  # 获取Alax发来的 物料名称
        pandian_date = models.Inventory.objects.filter(Q(name=name) & Q(
            inventoryDate__lt=out_date)).last().inventoryDate

        # print('出库日期：', out_date, '名称：', name)
        # 判断出库日期以后是进行过盘点，如果有则不得出库
        exists = models.Inventory.objects.filter(Q(name=name) & Q(
            inventoryDate__gte=out_date)).exists()
        # print(exists)
        if exists:
            return JsonResponse({"status": False, 'tips': "该日期已经盘点完毕，此日期不得出库！"})

        # 判断是否有库存，判断库存量是否满足出库量
        exists_pandian = models.Inventory.objects.filter(Q(name=name) & Q(
            inventoryDate__lt=out_date)).exists()
        if not exists_pandian:  # 如果没有找到此物料早于出库时间的盘点数据，
            exists_ruku = models.Warehousing.objects.filter(Q(warehousing_name=name) & Q(
                warehousing_date__lt=out_date)).exists()
            if not exists_ruku:  # 如果到此物料出库时间以前没有入库数据：
                return JsonResponse({"status": False, 'tips': "库存数量不足，请重新录入"})

        # ---------- 本期入库数量（未审核的入库单将不计入入库） ----------
        sum_quantity_dict = models.Warehousing.objects.filter(
            Q(warehousing_name=name) & Q(warehousing_date__range=(pandian_date, out_date)) & Q(
                approved=1)).aggregate(a=Sum('quantity'))
        if sum_quantity_dict['a']:
            sum_quantity = sum_quantity_dict['a']
        else:
            sum_quantity = 0

        # ---------- 盘点表盘点数量 ----------
        inventoryQuantity = models.Inventory.objects.filter(Q(name=name) & Q(
            inventoryDate__lt=out_date)).last().inventoryQuantity
        if not inventoryQuantity:
            inventoryQuantity = 0

        # ---------- 本期出库数量（未审核的出库单将计入出库） ----------
        sum_outbound_dict = models.outbound.objects.filter(
            Q(name=name) & Q(date__range=(pandian_date, out_date))).aggregate(aa=Sum('outbound'))
        if sum_outbound_dict['aa']:
            sum_outbound = sum_outbound_dict['aa']
        else:
            sum_outbound = 0
        # print('本期出库数量：', sum_outbound, type(sum_outbound))

        # ---------- 校验出库数量是否小于库存数量，小于库存数则继续计算 ----------
        # 合计库存数量 = 上次盘点数量 + 本期入库合计数量 -本期出库合计数量
        all_quantity = sum_quantity + inventoryQuantity - sum_outbound
        # print('合计库存数量：', all_quantity, type(all_quantity))
        if outbound < all_quantity:
            issueUnitPrice = orw_object.issueUnitPrice  # 获取已保存的数据：出库单价
            issueAmount = outbound * issueUnitPrice  # 计算 出库金额
            form.instance.issueAmount = issueAmount  # 修改出库金额，原有数据不变，用户提交的修改数据不变
            form.save()
            return JsonResponse({"status": True})
        else:
            error_text = '库存数量为：' + str(all_quantity) + '，不够出库数量。请重新录入'
            return JsonResponse({"status": False, 'tips': error_text})
    return JsonResponse({"status": False, 'error': form.errors})


@csrf_exempt
def outbound_print(request):
    """ 打印出库单 AJax请求
    1、后端查询数据后，把queryset数据，经过list，转成列表
    2、遍历列表处理数据，
    3、发送到前端数据
    4、前端把数据增加到窗口列表
    """
    data = request.POST
    date = data.get('date')
    department = data.get('department')

    if department:
        printobject = models.outbound.objects.filter(
            Q(date=date) & Q(department=department)).values()
        if printobject:
            printlist = list(printobject)  # 把Queryset转成列表
            for dict in printlist:  # 遍历列表中的字典，新增并删除无用数据
                id = dict['name_id']  # 提取字典中KEY对应的值
                batchCode = dict['batchCode']  # 提取字典中KEY对应的值
                name = models.Material.objects.filter(id=id).first().name  # 获取物料名称
                unit = models.Material.objects.filter(id=id).first().unit  # 获取计量单位
                dict['name'] = name  # 给字典赋值一个新的数据：('name':name)
                dict['unit'] = unit  # 给字典赋值一个新的数据：('unit':unit)
                dict['batchCode'] = batchCode  # 给字典赋值一个新的数据：('unit':unit)

                del dict['date']  # 删除字典中的一项
                del dict['department_id']  # 删除字典中的一项
                del dict['operator_id']  # 删除字典中的一项
                del dict['name_id']  # 删除字典中的一项
                del dict['approved']  # 删除字典中的一项

                # print(list(printobject))

            return JsonResponse({"status": True, "PRINT_QUERYSET": list(printobject)})
        else:
            error_text = '没有出库数据。请重新录入'
            return JsonResponse({"status": False, 'tips': error_text})
    error_text = '没有出库数据。请重新录入'
    return JsonResponse({"status": False, 'tips': error_text})
