import re
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import uvicorn

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 火山引擎API配置
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
API_KEY = "1ad45853-a28a-4508-80f9-9699dffb3761"

@app.post("/generate")
async def generate_name(user_input: dict):
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                },
                json={
                    "model": "deepseek-r1-250120",
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个中文名字生成专家，请严格按以下要求生成：1.必须返回合法JSON数组，包含三个对象 2.每个对象包含字段：chinese(中文名)、pinyin(拼音)、chinese_meaning(中文寓意)、english_meaning(英文寓意)、meme(网络梗) 3.JSON格式必须正确，不允许有任何注释或未闭合符号 4.示例格式：[{\"chinese\":...}]"
                        
                        },
                        {
                            "role": "user",
                            "content": f"请为英文名'{user_input['name']}'生成三个有趣的中文名字"
                        }
                    ],
                    "max_tokens": 2000
                }
            )
            if response.status_code != 200:
                print(f'API异常响应: {response.status_code} {response.text}')
                raise HTTPException(status_code=502, detail='上游服务异常')
            
            print(f'原始响应内容：{response.text}')  # 新增原始响应体记录
            result = response.json()
            print(f'结构化后的响应对象：{result}')
            
            if not result.get('choices') or not result['choices'][0].get('message'):
                raise HTTPException(status_code=502, detail='无效的API响应格式')
            
            # 强化清洗逻辑
            raw_content = result['choices'][0]['message']['content']
            cleaned_content = re.sub(r'(?i)(^\s*```(?:json)?\s*|\s*```\s*$)', '', raw_content, flags=re.MULTILINE).strip()
            cleaned_content = re.sub(r'[\x00-\x1F\x7F]', '', cleaned_content)  # 移除控制字符
            cleaned_content = re.sub(r'//.*?\n|#.*?\n', '\n', cleaned_content)  # 移除行注释

            print(f'清洗后JSON字符串：{cleaned_content}')  # 新增清洗后内容记录
            # 数据结构验证
            try:
                parsed_data = json.loads(cleaned_content)
                print(f'解析后的数据结构：{type(parsed_data)} 长度：{len(parsed_data)}')  # 新增解析结果记录
                if not isinstance(parsed_data, list) or len(parsed_data) != 3:
                    raise ValueError('需要包含3个对象的数组')
                
                required_fields = {'chinese', 'pinyin', 'chinese_meaning', 'english_meaning'}
                for i, item in enumerate(parsed_data):
                    if not all(field in item for field in required_fields):
                        missing = required_fields - item.keys()
                        print(f'第{i+1}个对象缺失字段：{missing} 完整对象：{item}')  # 新增详细错误日志
                        raise ValueError(f'第{i+1}个对象缺少字段：{missing}')
                        
            except json.JSONDecodeError as e:
                error_msg = f'JSON解析失败: 行{e.lineno}列{e.colno} - {e.msg}\n错误上下文: {cleaned_content[e.pos-15:e.pos+15]}'
                print(f'详细解析错误: {error_msg}')
                raise HTTPException(status_code=502, detail=error_msg)
            except ValueError as e:
                print(f'数据结构验证失败: {cleaned_content}')
                raise HTTPException(status_code=502, detail=f'数据结构错误: {str(e)}')
            
            return {"data": parsed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)