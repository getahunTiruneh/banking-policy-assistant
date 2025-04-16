import os
import PyPDF2
from docx import Document
from openai import OpenAI
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

class DocumentProcessor:
    def __init__(self, documents_dir='policy_documents'):
        self.documents_dir = documents_dir
        self.chunks = []
        self.embeddings = []
        self.document_index = []
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def load_documents(self):
        """Load and process all documents in the directory"""
        for filename in os.listdir(self.documents_dir):
            if filename.startswith('.'):
                continue
            filepath = os.path.join(self.documents_dir, filename)
            try:
                if filename.endswith('.pdf'):
                    text = self._extract_text_from_pdf(filepath)
                elif filename.endswith('.docx'):
                    text = self._extract_text_from_docx(filepath)
                elif filename.endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                else:
                    continue
                
                self._chunk_document(text, filename)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    def _extract_text_from_pdf(self, filepath):
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    def _extract_text_from_docx(self, filepath):
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def _chunk_document(self, text, filename, chunk_size=1000):
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            self.chunks.append(chunk)
            self.document_index.append({
                'filename': filename,
                'chunk_num': len(self.chunks),
                'start_word': i,
                'end_word': min(i+chunk_size, len(words))
            })
    
    def generate_embeddings(self):
        """Generate OpenAI embeddings for all chunks"""
        for i, chunk in enumerate(self.chunks):
            response = self.client.embeddings.create(
                input=chunk,
                model="text-embedding-3-small"
            )
            self.embeddings.append(response.data[0].embedding)
            if (i+1) % 10 == 0:
                print(f"Processed {i+1}/{len(self.chunks)} chunks")
    
    def save_model(self, output_dir='trained_model'):
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, 'chunks.pkl'), 'wb') as f:
            pickle.dump(self.chunks, f)
        with open(os.path.join(output_dir, 'embeddings.pkl'), 'wb') as f:
            pickle.dump(self.embeddings, f)
        with open(os.path.join(output_dir, 'document_index.pkl'), 'wb') as f:
            pickle.dump(self.document_index, f)
    
    def load_model(self, model_dir='trained_model'):
        with open(os.path.join(model_dir, 'chunks.pkl'), 'rb') as f:
            self.chunks = pickle.load(f)
        with open(os.path.join(model_dir, 'embeddings.pkl'), 'rb') as f:
            self.embeddings = pickle.load(f)
        with open(os.path.join(model_dir, 'document_index.pkl'), 'rb') as f:
            self.document_index = pickle.load(f)
    
    def query(self, question, top_n=3):
        """Find relevant document chunks for a question"""
        response = self.client.embeddings.create(
            input=question,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding
        
        similarities = cosine_similarity(
            [query_embedding],
            self.embeddings
        )[0]
        
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        return [(self.chunks[i], similarities[i], self.document_index[i]) 
                for i in top_indices]