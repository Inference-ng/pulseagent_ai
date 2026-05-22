import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import pickle

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../processed"))
    os.makedirs(base_dir, exist_ok=True)
    
    csv_path = os.path.join(base_dir, "amazon_fashion.csv")
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found. Run loader.py first.")
        return
        
    df = pd.read_csv(csv_path)
    items = df.to_dict('records')
    
    print(f"Loading {len(items)} items...")
    
    texts = [f"{item.get('name', '')} {item.get('description', '')}" for item in items]
    
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Embedding items...")
    embeddings = model.encode(texts)
    
    print("Building FAISS index...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    faiss.write_index(index, os.path.join(base_dir, 'items.index'))
    
    metadata = {i: item for i, item in enumerate(items)}
    with open(os.path.join(base_dir, 'items_metadata.pkl'), 'wb') as f:
        pickle.dump(metadata, f)
        
    print("Done building index and metadata.")

if __name__ == "__main__":
    main()
