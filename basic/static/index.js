const container = document.querySelector(".container");

document.getElementById("ask-btn").addEventListener("click", function() {
    fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_input: '請問 AI 是什麼？' })  // 確保是 JSON 格式
    })
    .then(response => response.json())
    .then(data => {
        if (data.response) {
            container.innerHTML += `<p>${data.response}</p>`;
        } else if (data.error) {
            container.innerHTML += `<p style="color: red;">錯誤：${data.error}</p>`;
        } else {
            container.innerHTML += `<p style="color: red;">未知錯誤</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        container.innerHTML += `<p style="color: red;">連線錯誤</p>`;
    });
});
