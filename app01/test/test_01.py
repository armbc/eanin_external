import requests

API_KEY = 'o9TqkiFs.dSzA8GeXP5neLkbX47wWrEm7KXtRM2fE'  # 替换为实际的API Key
V3_API_URL = 'http://www.mbcai.top/api/products/'
# V3_API_URL = 'https://mbcai.top/api/products/1/'

headers = {
    'Authorization': f'Api-Key {API_KEY}'
}

response = requests.get(V3_API_URL, headers=headers)

print(f"Response status code: {response.status_code}")
print(f"Response content: {response.text}")  # 打印响应内容

if response.status_code == 200:
    products = response.json()
    print(products)
    # 在V2中处理products数据，例如在模板中渲染
else:
    print(f"Error fetching products: {response.status_code}")

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""
url = "https://mbcai.top/api/products/"
headers = {"Authorization": "Api-Key HY0XzRcm.lNiv4lgq52pDq2L9Dk41iJH2i6OJfmM4"} #  替换 kjsd-xxxxx 为你的实际 API 密钥

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 如果请求失败，则引发异常
    products = response.json()
    print(products)
except requests.exceptions.RequestException as e:
    print(f"Error fetching products: {e}")

"""