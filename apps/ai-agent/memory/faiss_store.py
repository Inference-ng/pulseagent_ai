import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class FAISSStore:
    def __init__(self, index_path: str = None, metadata_path: str = None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/processed"))
        self.index_path = index_path or os.path.join(base_dir, "items.index")
        self.metadata_path = metadata_path or os.path.join(base_dir, "items_metadata.pkl")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.metadata = {}  # index_id -> dict
        
        self.load()
        
    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            # Initialize empty IndexFlatL2
            self.index = faiss.IndexFlatL2(384) # all-MiniLM-L6-v2 dim is 384
            self.metadata = {}

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)

    def add_items(self, items: List[Dict[str, Any]]):
        if not items:
            return
            
        texts = [f"{item.get('name', '')} {item.get('description', '')}" for item in items]
        embeddings = self.model.encode(texts)
        
        start_id = len(self.metadata)
        for i, item in enumerate(items):
            self.metadata[start_id + i] = item
            
        self.index.add(embeddings)
        self.save()

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        if self.index is None or self.index.ntotal == 0:
            return []
            
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.metadata:
                item = self.metadata[idx].copy()
                item['_distance'] = float(distances[0][i])
                results.append(item)
                
        return results
