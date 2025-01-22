from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chains import RetrievalQA
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

# 初始化資料庫與嵌入模型
db_path = os.path.join(os.path.dirname(__file__), 'db', 'temp')
if not os.path.exists(db_path):
    os.makedirs(db_path)

embeddings = OpenAIEmbeddings(api_key=openai_api_key)
vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)

# 載入 data.docx 並嵌入到向量資料庫
data_docx_path = os.path.join(os.path.dirname(__file__), 'data.docx')
if os.path.exists(data_docx_path):
    doc = Document(data_docx_path)
    texts = [para.text for para in doc.paragraphs if para.text.strip()]
    vectorstore.add_texts(texts)
    print("Successfully added document content to vector database.")
else:
    print(f"Error: 'data.docx' not found at {data_docx_path}")

# 初始化 OpenCC 轉換器
cc = OpenCC('s2t')  # 簡轉繁

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        user_input = request.json.get('user_input')
        if not user_input:
            return jsonify({'error': 'No user input provided'})

        # 使用向量檢索找到相關內容
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5, api_key=openai_api_key)
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        # 執行檢索與回答
        response = qa_chain.run(user_input)

        # 將回應轉為繁體中文
        answer = cc.convert(response)
        return jsonify({'response': answer})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
