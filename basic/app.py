from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from opencc import OpenCC
from docx import Document

# 載入 .env 環境變數
load_dotenv()

# 設定 OpenAI API Key
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

app = Flask(__name__, static_folder='static', template_folder='templates')
chat_history = []

# 載入 data.docx 內容
def load_docx_content(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    doc = Document(file_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

# 確保讀取正確的路徑
database_content = load_docx_content(os.path.join(os.path.dirname(__file__), 'basic', 'data.docx'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        user_input = request.json.get('user_input')
        if not user_input:
            return jsonify({'error': 'No user input provided'})

        # 簡單關鍵字搜尋
        if user_input.lower() in database_content.lower():
            return jsonify({'response': f'找到相關內容：{user_input}'})

        # 資料庫初始化
        db_path = os.path.join(os.path.dirname(__file__), 'db', 'temp')
        if not os.path.exists(db_path):
            os.makedirs(db_path)

        # 使用 GPT-4o 進行更深入的回答
        embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        db = Chroma(persist_directory=db_path, embedding_function=embeddings)
        docs = db.similarity_search(user_input)

        llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5, api_key=openai_api_key)
        chain = load_qa_chain(llm, chain_type="stuff")

        with get_openai_callback() as cb:
            response = chain.invoke({
                "input_documents": docs,
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
