document.getElementById("ask-btn").addEventListener("click", function () {
    const userInput = document.getElementById("user-input").value;

    if (!userInput) {
        alert("請輸入問題！");
        return;
    }

    const responseDiv = document.getElementById("response");

    // 顯示用戶的輸入
    const userBubble = document.createElement("div");
    userBubble.className = "chat-bubble user";
    userBubble.innerText = userInput;
    responseDiv.appendChild(userBubble);

    // 清空輸入框
    document.getElementById("user-input").value = "";

    // 傳送請求至後端
    fetch("/get_response", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_input: userInput }), // 傳送使用者輸入
    })
        .then((response) => response.json())
        .then((data) => {
            const assistantBubble = document.createElement("div");
            assistantBubble.className = "chat-bubble assistant";

            if (data.response) {
                assistantBubble.innerText = data.response;
            } else if (data.error) {
                assistantBubble.innerText = `錯誤：${data.error}`;
                assistantBubble.style.color = "red";
            }

            responseDiv.appendChild(assistantBubble);

            // 滾動到最新消息
            responseDiv.scrollTop = responseDiv.scrollHeight;
        })
        .catch((error) => {
            console.error("Error:", error);

            const errorBubble = document.createElement("div");
            errorBubble.className = "chat-bubble assistant";
            errorBubble.style.color = "red";
            errorBubble.innerText = "伺服器發生錯誤，請稍後再試！";
            responseDiv.appendChild(errorBubble);

            // 滾動到最新消息
            responseDiv.scrollTop = responseDiv.scrollHeight;
        });
});
