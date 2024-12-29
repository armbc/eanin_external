"""
本视图函数包括：
1、系统登陆单元
2、密码维护单元
"""

from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from app01 import models
from django import forms
from django.core.exceptions import ValidationError
from app01.utils.bootstrap import BootStrapModelForm
from app01.utils.encrypt import md5
from app01.utils.bootstrap import BootStrapForm
# from app01.utils.check_img import check_code
from io import BytesIO


class AdminModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)  # 插件widget 的作用是隐藏密码,render_value保留输入的密码
    )  # 创建字段

    class Meta:
        model = models.Admin  # models.py 中的类名
        fields = ['username', 'password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(render_value=True)  # 插件widget 隐藏密码的显示
        }

    # md5加密
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)  # 密码加密

    # 钩子函数验证密码是否一致。“self” 就是：cleaned_data 本身:验证之后返回的数据
    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))  # 确认密码加密
        if confirm != pwd:
            raise ValidationError('密码不一致。')
        return confirm  # 将数据放到 cleaned_data 中,return什么字段，数据库就保存什么


class AdminListModelForm(BootStrapModelForm):
    class Meta:
        model = models.Admin  # models.py 中的类名
        fields = ['username']


class SigninForm(BootStrapForm):
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput,
        required=True
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(render_value=True),  # True的意思是：保留用户填写的信息在对话框
        required=True
    )

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)


class UserSigninForm(BootStrapForm):
    name = forms.CharField(
        label='用户名',
        widget=forms.TextInput,
        required=True
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(render_value=True),  # True的意思是：保留用户填写的信息在对话框
        required=True
    )

    # 钩子方法：，将密码的明文改为密文。
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)


class UserModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)  # 插件widget 的作用是隐藏密码,render_value保留输入的密码
    )  # 创建字段

    class Meta:
        model = models.User  # models.py 中的类名
        fields = ['name', 'password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(render_value=True)  # 插件widget 隐藏密码的显示
        }

    # md5加密
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)  # 密码加密

    # 钩子函数验证密码是否一致。“self” 就是：cleaned_data 本身:验证之后返回的数据
    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))  # 确认密码加密
        if confirm != pwd:
            raise ValidationError('密码不一致。')
        return confirm  # 将数据放到 cleaned_data 中,return什么字段，数据库就保存什么


class UserChangePasswordModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)  # 插件widget 的作用是隐藏密码,render_value保留输入的密码
    )  # 创建字段

    class Meta:
        model = models.User  # models.py 中的类名
        fields = ['name', 'password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(render_value=True)  # 插件widget 隐藏密码的显示
        }

    # md5加密
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)  # 密码加密

    # 钩子函数验证密码是否一致。“self” 就是：cleaned_data 本身:验证之后返回的数据
    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))  # 确认密码加密
        if confirm != pwd:
            raise ValidationError('密码不一致。')
        return confirm  # 将数据放到 cleaned_data 中,return什么字段，数据库就保存什么


# -------------- 员工登陆、注销 -------------- #
def user_change_pwd(request):
    """ 修改密码 """
    title = '修改员工密码'
    row_object = models.User.objects.filter(id=1).first()
    if not row_object:  # 判断用户是否存在
        return redirect('/user/list01/')
    if request.method == 'GET':
        form = UserChangePasswordModelForm(instance=row_object)
        return render(request, 'user_change_pwd.html', {'form': form, "title": title})
    form = UserChangePasswordModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/user/list01/')
    return render(request, 'user_change_pwd.html', {"form": form, "title": title})


def user_sign_in(request):
    """ 员工登陆 """
    if request.method == "GET":
        form = UserSigninForm
        return render(request, "user_signin01.html", {'form': form})
    form = UserSigninForm(data=request.POST)
    if form.is_valid():
        # 验证成功，获取字典：用户名和密码
        # print(form.cleaned_data)
        # {'name': '李红霞', 'password': '123'}
        # 在UserSigninForm中添加钩子方法，将密码的明文改为密文。
        # {'name': '李红霞', 'password': 'b1b3f41638dee89db39743d838423ced'}
        # 去数据库获取用户对象，校验数据。如果错误，则返回空值None
        # return HttpResponse("ok")

        user_object = models.User.objects.filter(**form.cleaned_data).first()
        if not user_object:
            form.add_error("password", "用户名或密码错误")  # 主动在form中的密码下面添加错误信息
            return render(request, "user_signin01.html", {'form': form})
        # 如果用户填写的数据正确，下面一句话将cookie和session的注入完成。
        request.session["info"] = {"id": user_object.id, "name": user_object.name}
        return redirect("/index/home01/")
    return render(request, "user_signin01.html", {'form': form})


def user_sign_out(request):
    """ 注销 """
    request.session.clear()
    return redirect("/user_sign_in/")


# -------------- 管理员登陆、注销 -------------- #
def sign_in(request):
    """ 管理员登陆 """
    if request.method == "GET":
        form = SigninForm()
        return render(request, "admin_signin01.html", {'form': form})
    form = SigninForm(data=request.POST)
    if form.is_valid():
        admin_object = models.Admin.objects.filter(**form.cleaned_data).first()
        if not admin_object:
            form.add_error("password", "用户名或密码错误")
            return render(request, "admin_signin01.html", {'form': form})
        request.session["info"] = {"id": admin_object.id, "name": admin_object.username}
        return redirect("/index/home01/")
    return render(request, "admin_signin01.html", {'form': form})


def sign_out(request):
    """ 注销 """
    request.session.clear()
    return redirect("/sign_in/")


# def image_code(request):
#     """ 生成图片验证码 """
#     # 调用写好的check_img函数;调用一个内存中的对象(from io import BytesIO)，以便将图片写入内存
#     img, code_str = check_code()
#     print(code_str)
#
#     stream = BytesIO()  # 创建内存中的文件
#     img.save(stream, 'png')  # 将img写入该文件
#     return HttpResponse(stream.getvalue())


# -------------- 登陆、注销 end -------------- #


# -------------- 管理员管理 -------------- #
def admin_list01(request):
    form = AdminListModelForm()
    queryset = models.Admin.objects.all()
    context = {
        'queryset': queryset,
        'form': form
    }
    return render(request, "admin_list01.html", context)


def admin_add01(request):
    title = '增加管理员'
    form = AdminModelForm()
    queryset = models.Admin.objects.all()
    context = {
        'queryset': queryset,
        'form': form,
        'title': title
    }
    if request.method == "GET":
        return render(request, "add_model.html", context)
    # 校验数据是否合法：
    form = AdminModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/admin/list01/')
    return render(request, 'add_model.html', {'queryset': queryset, 'form': form, 'title': title})


def admin_edit01(request, nid):
    """ 编辑管理员 """
    title = '编辑管理员'
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:  # 判断用户是否存在
        return redirect('/admin/list01/')
    if request.method == 'GET':
        form = AdminModelForm(instance=row_object)
        return render(request, 'admin_edit01.html', {'form': form, "title": title})
    form = AdminModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/admin/list01/')
    return render(request, 'admin_edit01.html', {"form": form, "title": title})


def admin_delete01(request):
    """删除管理员"""
    uid = request.GET.get('uid')
    exists = models.Admin.objects.filter(id=uid).exists()
    if not exists:  # 判断用户是否存在
        return JsonResponse({"status": False, 'error': "数据不存在,删除失败"})
    models.Admin.objects.filter(id=uid).delete()
    return JsonResponse({"status": True})

# -------------- 管理员管理 end-------------- #
