const container = document.querySelector(".container");

document.getElementById("ask-btn").addEventListener("click", function() {
    fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ user_input: '請問 AI 是什麼？' })
    })
    .then(response => response.json())
    .then(data => {
        container.innerHTML += `<p>${data.response}</p>`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
