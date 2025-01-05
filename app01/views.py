from django.shortcuts import render
import os
import requests
from django.urls import reverse

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
        return None  # 或返回空列表 []


# -------------- 首页 -------------- #
def index(request):
    cakes = [
        {"name": "巧克力蛋糕", "image": "img/images/cake/女王蛋糕.webp", "url": reverse('cake_choco')},
        {"name": "水果蛋糕", "image": "img/images/cake/女王蛋糕.webp", "url": "#"},
        {"name": "奶油蛋糕", "image": "img/images/cake/女王蛋糕.webp", "url": "#"},
        {"name": "儿童蛋糕", "image": "img/images/cake/女王蛋糕.webp", "url": "#"},
        {"name": "节日蛋糕", "image": "img/images/cake/女王蛋糕.webp", "url": "#"},
    ]
    context = {'cakes': cakes}
    return render(request, 'index.html', context)


# -------------- 获取巧克力蛋糕 -------------- #
def cake_choco(request):
    """首页 从 V3 获取 "cake" 类别下 "choco-" 开头的产品数据"""
    v3_api_url = "https://mbcai.top/api/products/"
    params = {"category": "cake", "prefix": "choco-"}
    products_data = get_data_from_v3(v3_api_url, params=params)
    # 筛选数据
    filtered_products = []
    if products_data:
        for product in products_data:
            if product.get("is_available", True):  # 保留 is_available 为 True 的项
                new_product = {}
                for key, value in product.items():
                    if key not in ("id", "product_code", "category", "supplier", "is_available"):
                        new_product[key] = value
                filtered_products.append(new_product)
    context = {
        "products": filtered_products if filtered_products else [],  # 简化条件表达式
    }
    print(context)
    return render(request, "cake_choco.html", context)


# ------ 测试专用 ------
"""
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
"""
