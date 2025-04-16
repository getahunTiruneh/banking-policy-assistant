from document_processor import DocumentProcessor

def main():
    print("Starting model training...")
    processor = DocumentProcessor()
    processor.load_documents()
    print(f"Loaded {len(processor.chunks)} document chunks")
    processor.generate_embeddings()
    processor.save_model()
    print("Model training completed successfully!")

if __name__ == "__main__":
    main()