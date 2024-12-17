const container = document.querySelector(".container");

document.addEventListener('DOMContentLoaded', function() {
    fetch('/hello', {
    method: 'POST', // 使用 POST 請求
    headers: {
    'Content-Type': 'text/plain',
    },
    body: JSON.stringify({}) // 要傳遞的訊息
    })
    .then(response => response.json())
    .then(data => {
    // 後端返回的訊息之後的動作
        container.innerHTML = `<p>${data.message}</p>`;
    })
    .catch(error => {
   //例外錯誤狀況處理
    console.error('Error:', error);
    });
});
   