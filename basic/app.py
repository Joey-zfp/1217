from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from opencc import OpenCC
from docx import Document  # 新增 docx 支援
import openai

# ✅ 載入環境變數
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__, static_folder='static', template_folder='templates')
chat_history = []

# ✅ 修正：先定義 load_docx_content 函式
def load_docx_content(file_path):
    if not os.path.exists(file_path):
        print(f"⚠️ 檔案不存在：{file_path}")
        return "❌ 無法載入資料，請確認檔案是否存在。"

    doc = Document(file_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

# ✅ 設定正確的檔案路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCX_PATH = os.path.join(BASE_DIR, 'basic', 'data.docx')

# ✅ 載入資料
database_content = load_docx_content(DOCX_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        user_input = request.json.get('user_input')
        if not user_input:
            return jsonify({'error': 'No user input provided'})

        # 🔍 關鍵字搜尋
        if user_input.lower() in database_content.lower():
            return jsonify({'response': f'找到相關內容：{user_input}'})

        # 🧠 使用 GPT-4o 進行回答
        llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5)
        chain = load_qa_chain(llm, chain_type="stuff")

        with get_openai_callback() as cb:
            response = chain.invoke({
                "input_documents": [database_content],
                "question": user_input
            }, return_only_outputs=True)

        cc = OpenCC('s2t')
        answer = cc.convert(response['output_text'])
        chat_history.append({'user': user_input, 'assistant': answer})

        return jsonify({'response': answer})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
