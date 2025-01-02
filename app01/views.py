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


def index_api_key(request):
    api_key = os.environ.get('mbcai_api_key')
    return render(request, 'index.html', {'api_key': api_key})


# -------------- 首页 -------------- #
def index(request):
    """首页"""
    return render(request, "index.html")


# -------------- 首页end -------------- #


# ------ 测试专用 ------

def test_api(request):
    api_key = os.environ.get('MBCAI_API_KEY')  # 获取环境变量

    if not api_key:
        return HttpResponse("Error: MBCAI_API_KEY environment variable not set.", status=500) # 添加超时设置

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