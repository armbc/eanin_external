from django.shortcuts import render
import os
from django.http import HttpResponse
import requests

# -------------- 从环境变量中获取APIkey，渲染一个JavaScript变量api_key
"""
前端模板用法：
<!-- V2的index.html -->
<script>
    const v3ApiKey = "{{ api_key }}"; // Django模板变量

    fetch('https://mbcai.top/api/products/', {
        headers: {
            'Authorization': 'Api-Key ' + v3ApiKey
        }
    })
    // ... rest of your fetch code
</script>
"""


# ------- 封装`get_data_from_v3` 函数,在不同的视图函数中轻松地调用
def get_data_from_v3(url, params=None):
    """
    从 V3 获取数据的辅助函数

    Args:
        url: V3 API 的 URL
        params: 可选的查询参数 (字典)

    Returns:
        如果请求成功，返回 JSON 数据；如果失败，返回 None 并打印错误信息。
    """
    api_key = os.environ.get("MBCAI_API_KEY")
    if not api_key:
        print("Error: MBCAI_API_KEY environment variable not set.")
        return None

    headers = {
        "Authorization": f"Api-Key {api_key}"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # 抛出 HTTPError 异常以进行错误处理
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from V3: {e}")
        return None


# -------------- 首页 -------------- #
def index(request):
    """首页 从 V3 获取产品数据并按分类展示 """
    v3_api_url = "https://mbcai.top/api/products/"

    categories = ["cake", "bread", "dessert"]   # 定义需要获取的类别
    products_by_category = {}

    for category in categories: # 使用循环遍历 `categories` 列表，避免重复代码
        params = {"category": category}
        products_data = get_data_from_v3(v3_api_url, params=params)

        if products_data:
            products_by_category[category] = products_data

    context = {
        "products_by_category": products_by_category,
    }
    print(context)
    return render(request, "index.html", context)


# -------------- 首页end -------------- #


# -------------- 蛋糕分类 -------------- #
def cake_list(request):
    # 获取API key
    api_key = os.environ.get('MBCAI_API_KEY')  # 获取环境变量
    headers = {'Authorization': f'Api-Key {api_key}'}

    # 从 V3 获取产品数据
    url = "http://www.mbcai.top/api/products/"  # 替换为你的 V3 API 地址
    # print(api_key)
    try:
        response = requests.get(url, headers=headers)  # 设置超时时间
        response.raise_for_status()  # 如果状态码不是 2xx，则引发 HTTPError 异常
        products = response.json()
    except requests.exceptions.RequestException as e:
        # 处理异常，例如记录错误日志，返回错误页面等
        print(f"Error fetching product data: {e}")  # 调试期间打印错误信息
        return render(request, 'error.html', {'error_message': '无法获取产品数据。'}, status=500)  # 返回错误页面

    cakes = [product for product in products if product.get('category') == 'cake']  # 使用 get() 方法避免 KeyError
    print(cakes)
    return render(request, 'cake_list.html', {'products': cakes})


# -------------- 蛋糕分类 end -------------- #


# ------ 测试专用 ------

def test_api(request):
    api_key = os.environ.get('MBCAI_API_KEY')  # 获取环境变量

    if not api_key:
        return HttpResponse("Error: MBCAI_API_KEY environment variable not set.", status=500)  # 添加超时设置

    print(api_key)
    v3_api_url = 'http://www.mbcai.top/api/products/'
    headers = {
        'Authorization': f'Api-Key {api_key}'
    }

    try:
        response = requests.get(v3_api_url, headers=headers, timeout=5)
        response.raise_for_status()  # 如果状态码不是2xx，则引发HTTPError异常

        products = response.json()
        #  在这里处理 products 数据，例如序列化为 JSON 字符串
        return HttpResponse(response.content, content_type="application/json")

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error: {e}", status=500)
