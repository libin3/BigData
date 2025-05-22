我希望做一个帮助外国人起有趣中文名的网站，核心功能是：
1. 外国人输入它的英文名
2. 点击生成按钮
3. AI生成三个中文名
4. 每个中文名都能体现出中国文化，并给出中英文分别的寓意解释
5. 理解英文名字的含义，然后生成中文名字，并且有幽默成分，适当可以加一些梗
接入火山引擎的DeepSeek R1 API，使用AI来给外国人起中文名，实现上面的功能。

为了简单实现，API key就以明文的形式写在前端页面即可，以下是API相关信息：
1. API key：1ad45853-a28a-4508-80f9-9699dffb3761
2. 参考的调用指南
curl https://ark.cn-beijing.volces.com/api/v3/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer 23aeb5da-793c-4eda-1122-8eec47a001dd" \
-d '{
    "model": "deepseek-r1-250120",
"messages": [
    {"role": "system","content": "你是豆包，是由字节跳动开发的 AI 人工智能助手."},
    {"role": "user","content": "常见的十字花科植物有哪些？"}
]}'

注意：API请求超时设置为60秒，且用后端fastAPI+uvicorn框架框架调用。
使用简单的HTML、CSS和JavaScript实现，并通过Python的fastAPI+uvicorn框架搭建一个后端服务来处理API调用，确保安全和跨域问题得到妥善处理。

1、封装命令
2、打印输出报错：直接 curl 才能看到真实的报错原因
能不能优化下现有的目录结构
3、请求接口，前端拿不到数据，可能是解析不正确
4、前端请求接口，后端返回加工好的数据。前端拿到数据，显示到页面，尽量不做复杂加工。
5、在关键位置打印信息，确保后续发现问题；
6、2 个大模型循环验证，减少出错频率： 
7、大模型 stream: False
8、为接口增加summary、response_description、tags和responses参数


curl --location --request POST 'https://api.coze.cn/v3/chat 
--header 'Authorization: Bearer pat_pXkNqiH8L2jsGOZIBOGdOwcnUbnkhDnP7Uxuq9QAiEUP4pV4AncYeEUGsthi4vmh' \ 
--header 'Content-Type: application/json' \ 
--data-raw '{ "bot_id": "7506838151005650978", "user_id": "123456789", "stream": true, "auto_save_history":true, "additional_messages": [{"role":"user","content":"可爱","content_type":"text"}]}' 





-- 调用工作流
curl --location --request POST 'https://api.coze.cn/v1/workflow/run' \
--header 'Authorization: Bearer pat_ZNoYakst2i3lI0TscOKW6EwGXNV5FrrAmtby6XP64HfD4OFAV5dMFW8TFFIeMDcB' \
--header 'Content-Type: application/json' \
--data-raw '{
  "user_id": "123456789",
  "stream": false,
  "is_async": false,
  "workflow_id": "7498939499705057290",
  "parameters": {"input":"可爱"}
}'

在现有技术架构基础上，再写一个js脚本，前端请求脚本时，将发送的内容带入到参数content，调用上面的API，再写一个前端配套测试API调用的html页面，注意这个API是流式返回。

curl -X POST http://localhost:8000/coze-chat \
-H "Content-Type: application/json" \
-H "Authorization: Bearer pat_ZNoYakst2i3lI0TscOKW6EwGXNV5FrrAmtby6XP64HfD4OFAV5dMFW8TFFIeMDcB" \
-d '{"messages":[{"input":"可爱"}]}'
