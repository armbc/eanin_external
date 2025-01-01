from django.shortcuts import render
import os

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
