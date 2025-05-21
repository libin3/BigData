async function generateNames() {
  const name = document.getElementById('englishName').value.trim();
  const resultDiv = document.getElementById('result');
  
  if (!name) {
    resultDiv.innerHTML = `<div class='error'>请输入英文名</div>`;
    return;
  }

  try {
    resultDiv.innerHTML = `<div class='loading'>生成中...</div>`;
    
    const response = await fetch('http://localhost:8000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });

    if (!response.ok) {
        throw new Error(`请求失败: ${response.status} ${response.statusText}`);
    }
    const { data: names, error } = await response.json();
    if (error) {
        throw new Error(error);
    }
    if (!Array.isArray(names)) {
        throw new Error('无效的响应格式：期待数组');
    }

    // 字段完整性验证
    const requiredFields = ['chinese', 'pinyin', 'chinese_meaning', 'english_meaning'];
    names.forEach((item, index) => {
        const missingFields = requiredFields.filter(field => !(field in item));
        if (missingFields.length > 0) {
            throw new Error(`第${index + 1}个名字缺少字段：${missingFields.join(', ')}`);
        }
    });
    resultDiv.innerHTML = names.map(n => `
        <div class='name-card'>
          <h3>${n.chinese} (${n.pinyin})</h3>
          <p>中文寓意：${n.chinese_meaning}</p>
          <p>English：${n.english_meaning}</p>
          ${n.meme ? `<small class='meme'>🎉 ${n.meme}</small>` : ''}
        </div>
      `).join('');
  // 添加请求超时处理
  const controller = new AbortController();
  setTimeout(() => controller.abort(), 10000);
  
  // 在catch块中增加错误分类处理
  } catch (error) {
    let message = error.message;
    if (error.name === 'AbortError') {
      message = '请求超时，请重试';
    } else if (error instanceof SyntaxError) {
      message = '数据解析失败，请检查API响应格式';
    }
    resultDiv.innerHTML = `<div class='error'>
      <p>生成失败: ${message}</p>
      <button onclick="generateNames()">🔄 重试</button>
      <details style="margin-top:10px">
        <summary>查看详情</summary>
        <pre>${error.message}</pre>
      </details>
    </div>`;
  }
}