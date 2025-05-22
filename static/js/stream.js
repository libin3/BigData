// 删除processEvent函数及相关流式处理逻辑
const decoder = new TextDecoder();

// 修改后的请求函数
function startStream() {
    const inputText = document.getElementById('inputText').value;
    fetch('/coze-chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            messages: [{
                input: inputText
            }]
        })
    })
    .then(response => response.json())
    .then(data => processServerResponse(data))
    .catch(error => console.error('请求失败:', error));
}