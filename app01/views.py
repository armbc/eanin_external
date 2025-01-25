from django.shortcuts import render,  HttpResponse
import os
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

    # print(params)

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # 抛出 HTTPError 异常以进行错误处理
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from V3: {e}")
        return None  # 或返回空列表 []


# -------------- 首页 -------------- #
"""首页 从 V3 获取 "cake" 类别下sub_category小类的产品数据"""
def index(request):
    v3_api_url = "https://mbcai.top/api/categories/"
    v3_data = get_data_from_v3(v3_api_url)
    # print(v3_data)

    context = {}
    if v3_data:
        context['categories'] = v3_data.get('categories', [])
        context['cake_subcategories'] = v3_data.get('cake_subcategories', [])
    else:
        # 处理 V3 数据获取失败的情况，例如显示错误消息或使用默认数据
        context['categories'] = []
        context['cake_subcategories'] = []
        context['error_message'] = "无法从 服务器 获取数据。"

    # print(context)
    return render(request, 'index.html', context)


# -------------- 获取蛋糕 -------------- #
def products(request):
    # category = request.GET.get('category')
    category = request.GET.get('category')
    subcategory = request.GET.get('subcategory')
    subcategory_name = request.GET.get('subcategory_name')
    # print(subcategory_name)

    params = {}
    if category:
        params['category'] = category
    if subcategory:
        params['subcategory'] = subcategory
    if subcategory_name:
        params['subcategory_name'] = subcategory_name

    products_url = 'https://mbcai.top/api/products/'
    # print(products_url, params)
    products_data = get_data_from_v3(products_url, params=params)
    # print(products_data)

    if products_data is None:
        # 如果没有收到 products_data，返回 HttpResponse
        return HttpResponse("Failed to fetch products from V3.", status=500)
    else:
        # 如果返回了空数据，传送空的 products_data
        if not products_data:
            products_data = []  # 传递空列表

        # 构造完整的图片 URL
        for product in products_data:
            product['main_image'] = f"https://mbcai.top{product['main_image']}"  # 构造完整的图片 URL
            product['secondary_image1'] = f"https://mbcai.top{product['secondary_image1']}"  # 构造完整的图片 URL
            product['secondary_image2'] = f"https://mbcai.top{product['secondary_image2']}"  # 构造完整的图片 URL

        context = {'products': products_data, 'subcategory_name': subcategory_name}
        # print(context)
        return render(request, 'products.html', context)


    # 筛选数据


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
