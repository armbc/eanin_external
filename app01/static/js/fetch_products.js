fetch('https://mbcai.top/api/products/', {
    headers: {
        'Authorization': 'Api-Key v3ApiKey' // 使用你的JavaScript变量
    }
})
.then(response => response.json())
.then(data => {
    // 处理获取到的产品数据
    console.log(data);
    // 在前端展示产品信息和图片
    data.forEach(product => {
        const productElement = document.createElement('div');
        productElement.innerHTML = `
            <h3>${product.name}</h3>
            <img src="https://mbcai.top${product.main_image}" alt="${product.name}">
            <img src="https://mbcai.top${product.secondary_image1}" alt="${product.name}">
            <img src="https://mbcai.top${product.secondary_image2}" alt="${product.name}">
            <p>${product.description}</p>
            <p>Price: ${product.price}</p>
        `;
        document.body.appendChild(productElement); // 将产品信息添加到页面
    });
})
.catch(error => {
    console.error('Error fetching data:', error);
});
