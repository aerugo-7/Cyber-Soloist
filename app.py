import os
from flask import Flask, render_template, request, jsonify
import requests
from openai import OpenAI

# 路径自动处理
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')
app = Flask(__name__, template_folder=template_dir)

# --- 密钥填入处 ---
DEEPSEEK_KEY = "sk-125beb76c63b469485884a6a63deb157"
DIFY_API_KEY = "app-DKIeeZKDR95yBL9VDxEKn1mD" 

# 初始化 DeepSeek 客户端
client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")

@app.route('/')
def index():
    # 诊断：看看 Flask 到底在找哪个文件夹
    print(f"Flask 正在寻找的网页路径: {template_dir}")
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    user_query = request.json.get('query')
    print(f"收到请求: {user_query}")
    
    # 1. 调用 DeepSeek
    try:
        ds_resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"帮我写篇关于'{user_query}'的小红书笔记"}]
        )
        ds_out = ds_resp.choices[0].message.content
    except Exception as e:
        ds_out = f"DeepSeek 出错: {str(e)}"

# 2. 调用 Dify
    try:
        url = "https://api.dify.ai/v1/chat-messages"
        headers = {"Authorization": f"Bearer {DIFY_API_KEY}", "Content-Type": "application/json"}
        data = {
            "inputs": {},
            "query": user_query,
            "response_mode": "blocking",
            "user": "tester"
        }
        
        res = requests.post(url, headers=headers, json=data, timeout=120)
        # -----------------------------------------------

        if res.status_code == 200:
            rag_out = res.json().get('answer', "未找到内容")
        else:
            rag_out = f"Dify 报错: {res.text}"            
    except Exception as e:
        rag_out = f"网络错误: {str(e)}"

    return jsonify({"deepseek": ds_out, "cyber_soloist": rag_out})

if __name__ == '__main__':
    import os
    # 这里的 port 会由云平台自动分配，如果没有则默认为 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)