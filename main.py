import re
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# Coze接口请求模型
class CozeChatRequest(BaseModel):
    messages: List[Dict[str, Any]] = Field(..., example=[{"input": "可爱"}], description="用户输入消息列表")

# 名称生成请求模型
class GenerateNameRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, example="Alice", description="需要翻译的英文名")

# 名称生成响应模型
class NameOption(BaseModel):
    chinese: str
    pinyin: str
    chinese_meaning: str
    english_meaning: str
    meme: str = Field(default="")

class GenerateNameResponse(BaseModel):
    data: List[NameOption] = Field(...)

# Coze接口响应模型
class CozeChatResponse(BaseModel):
    data: dict = Field(..., description="包含原始响应和解析URL的数据结构")

# 加载环境变量
load_dotenv()
from fastapi.responses import StreamingResponse, FileResponse

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
COZE_API_URL = "https://api.coze.cn/v1/workflow/run"
COZE_API_KEY = os.getenv("COZE_API_KEY")
print(f'当前环境变量COZE_API_KEY: {COZE_API_KEY}')

@app.post(
    "/coze-chat",
    summary="处理Coze工作流请求",
    response_description="包含原始响应和解析后URL的数据结构",
    tags=["Coze API"],
    responses={
        200: {"description": "成功返回处理结果"},
        401: {"description": "身份验证失败"},
        502: {"description": "上游服务异常"},
        500: {"description": "服务器内部错误"}
    }
)
@app.post(
    "/coze-chat",
    response_model=CozeChatResponse,
    summary="处理Coze工作流请求",
    response_description="包含原始响应和解析后URL的数据结构",
    tags=["Coze API"]
)
async def coze_chat_stream(user_input: CozeChatRequest, request: Request):
    print('请求参数:', user_input)
    print(f'收到请求方法：{request.method} 路径：{request.url.path}\n请求头信息：{dict(request.headers)}')
    if not COZE_API_KEY:
        raise HTTPException(status_code=401, detail="Missing API credentials")
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                COZE_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {COZE_API_KEY}"
                },
                json={
                    "bot_id": "7506838151005650978",
                    "user_id": "123456789",
                    "stream": False,
                    "auto_save_history": True,
                    "is_async": False,
                    "workflow_id": "7498939499705057290",
                    "parameters": {"input":user_input.dict()},
                }
            )
            
            print(f'响应状态码: {response.status_code}')
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail='Coze API异常')
            
            # 提取并结构化返回数据
            response_data = response.json()
            print(f'完整响应内容：{response_data}')  # 调试完整响应体
            
            # 结构化数据校验
            try:
                parsed_data = json.loads(response_data['data'])
                if not isinstance(parsed_data, dict):
                    raise ValueError('Data字段应为字典类型')
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f'数据解析失败: {str(e)}')
                raise HTTPException(status_code=502, detail=f'无效的API响应格式: {str(e)}')
            
            raw_output = parsed_data.get('output', '')  # 从解析后的字典获取值
            print(f'原始输出内容：{raw_output}')  # 调试原始输出内容
            
            # 返回新的数据结构
            return CozeChatResponse(
                data={
                    "original": response_data,
                    "urls": raw_output
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/generate",
    summary="生成英文名对应中文名",
    response_description="包含三个中文名选项的数组",
    tags=["名称生成"],
    responses={
        200: {"description": "成功返回生成结果"},
        502: {"description": "上游服务异常"},
        500: {"description": "服务器内部错误"}
    }
)
# 更新后的路由装饰器
@app.post(
    "/generate",
    response_model=GenerateNameResponse,
    summary="生成英文名对应中文名",
    tags=["名称生成"]
)
async def generate_name(user_input: GenerateNameRequest) -> GenerateNameResponse:
    # 使用user_input.name代替原字典访问方式
    f"请为英文名'{user_input.name}'生成..."
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
                            "content": f"请为英文名'{user_input.name}'生成三个有趣的中文名字"
                        }
                    ],
                    "max_tokens": 2000
                }
            )
            print(f'响应状态码: {response.status_code}')
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
            
            return GenerateNameResponse(data=parsed_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 静态文件服务移到/static路径
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")

# 处理/coze-chat路径
@app.get("/coze-chat")
async def serve_coze_chat():
    return FileResponse("static/stream-test.html", media_type="text/html")

# 处理根路径
@app.get("/")
async def serve_home():
    return FileResponse("static/index.html", media_type="text/html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)