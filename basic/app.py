from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from opencc import OpenCC
from docx import Document as DocxDocument  # 避免名稱衝突
from langchain.schema import Document  # ✅ 新增這行

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__, static_folder='static', template_folder='templates')
chat_history = []

# 載入 docx 檔案
def load_docx_content(file_path):
    doc = DocxDocument(file_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

database_content = load_docx_content('basic/data.docx')  # 確保檔案路徑正確

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        user_input = request.json.get('user_input')
        if not user_input:
            return jsonify({'error': 'No user input provided'})

        # 將內容包裝成 Document 物件
        docs = [Document(page_content=database_content)]

        llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5)
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
