from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from opencc import OpenCC
import openai

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__, static_folder='static', template_folder='templates')
chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        user_input = request.json.get('user_input')  # 確認用 JSON 接收
        if not user_input:
            return jsonify({'error': 'No user input provided'})

        # 模擬簡單回應，先測試是否正常
        return jsonify({'response': f'你問了：「{user_input}」'})

    except Exception as e:
        return jsonify({'error': str(e)})


        embeddings = OpenAIEmbeddings()
        db = Chroma(persist_directory="./db/temp/", embedding_function=embeddings)
        docs = db.similarity_search(user_input)

        llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5)
        chain = load_qa_chain(llm, chain_type="stuff")

        with get_openai_callback() as cb:
            response = chain.invoke({"input_documents": docs, "question": user_input}, return_only_outputs=True)

        cc = OpenCC('s2t')
        answer = cc.convert(response['output_text'])
        chat_history.append({'user': user_input, 'assistant': response['output_text']})

        return jsonify({'response': answer})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
