from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect


class AuthMiddleware(MiddlewareMixin):
    """ 中间件 """

    def process_request(self, request):
        # 如果方法中没有返回值（即返回None），则继续运行。
        # 如果有返回值,一般都是返回 HttpResponse、render、redirect(给用户一个地址重定向)

        # 1.读取当前用户请求的url:request.path_info
        print(request.path_info)
        if request.path_info in ["/sign_in/", "/image/code/"]:

            return
        # 2.读取用户访问的session信息，如果可以读取，说明已经登陆过。
        info_dict = request.session.get("info")
        if info_dict:
            return
        # 3.如果没有返回信息，重定向到登陆页面
        return redirect('/sign_in/')

    def process_response(self, request, response):
        return response
