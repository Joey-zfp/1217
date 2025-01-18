document.getElementById("ask-btn").addEventListener("click", function() {
    const userInput = document.getElementById("user-input").value;

    if (!userInput) {
        alert("請輸入問題！");
        return;
    }

    fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_input: userInput })  // 傳送使用者輸入
    })
    .then(response => response.json())
    .then(data => {
        const responseDiv = document.getElementById("response");
        if (data.response) {
            responseDiv.innerHTML = `<p>${data.response}</p>`;
        } else if (data.error) {
            responseDiv.innerHTML = `<p style="color: red;">錯誤：${data.error}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
