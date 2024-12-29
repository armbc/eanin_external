""""
自定义分页组件
"""

from django.utils.safestring import mark_safe


class Pagination(object):
    """"
    request:请求的对象
    queryset:符合条件的数据，根据这个数据进行分页处理
    page_size:每页显示多少条数据
    page_param:在url里传递获得分页的参数，例如：/pretty/list/?page=12
    plus：显示当前页，前后或后几页（页码）

    """

    def __init__(self, request, queryset, page_size=10, page_param="page", plus=5):
        import copy
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict
        self.page_param = page_param

        page = request.GET.get(page_param, "1")

        if page.isdecimal():  # 判断是否是十进制的数
            page = int(page)
        else:
            page = 1
        self.page = page
        self.page_size = page_size

        self.start = (page - 1) * page_size
        self.end = page * page_size

        self.page_queryset = queryset[self.start:self.end]

        self.total_count = queryset.count()
        self.plus = plus

        total_page_count, div = divmod(self.total_count, self.page_size)  # 计算需要多少页

        if div:
            total_page_count += 1
        self.total_page_count = total_page_count

    def html(self):

        if self.total_page_count <= 2 * self.plus:  # 数据库中该表的行数比较少
            start_page = 1
            end_page = self.total_page_count
        else:
            # 数据库中该表的函数比较多
            if self.page <= 5:  # 小的极值 #判断当前页是小于5的
                start_page = 1
                end_page = 2 * self.plus
            else:
                if self.page + self.plus > self.total_page_count:  # 判断当前页是否超出总的页数
                    start_page = self.total_page_count - 2 * self.plus
                    end_page = self.total_page_count
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus

        page_str_list = []
        self.query_dict.setlist(self.page_param, [1])
        page_str_list.append('<li><a href="?{}">首页</a></li>'.format(self.query_dict.urlencode()))

        if self.page > 1:
            self.query_dict.setlist(self.page_param, [self.page - 1])
            prev = '<li><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [1])
            prev = '<li><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(prev)

        # 页面
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist(self.page_param, [i])
            if i == self.page:
                ele = '<li class="active"><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            else:
                ele = '<li><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            page_str_list.append(ele)

        # 下一页
        if self.page < self.total_page_count:
            self.query_dict.setlist(self.page_param, [self.page + 1])
            prev = '<li><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [self.total_page_count])
            prev = '<li ><a href="{}">下一页</a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(prev)

        # 尾页
        self.query_dict.setlist(self.page_param, [self.total_page_count])
        page_str_list.append('<li ><a href="?{}">尾页</a></li>'.format(self.query_dict.urlencode()))

        search_string = """ 
            <li>
                <form style="float: left;margin-left: 1px" method="get">
                    <input name="page" 
                            style="position: relative;float: left;display: inline-block;width: 80px;border-radius: 0px" 
                            type="text" class="form-control" placeholder="页码">
                    <button class="btn btn-default" style="border-radius: 0px" type="submit">跳转</button>
                </form>
            </li>
            """

        page_str_list.append(search_string)
        page_string = mark_safe("".join(page_str_list))
        return page_string
