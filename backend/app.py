from flask import Flask, request, jsonify
from document_processor import DocumentProcessor
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

processor = DocumentProcessor()
processor.load_model()

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        relevant_chunks = processor.query(question)
        context = "\n\n".join([chunk[0] for chunk in relevant_chunks])
        
        response = processor.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable banking policy assistant. Answer questions precisely based on the provided context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"}
            ],
            temperature=0.3
        )
        
        return jsonify({
            "answer": response.choices[0].message.content,
            "sources": [chunk[2]['filename'] for chunk in relevant_chunks]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)