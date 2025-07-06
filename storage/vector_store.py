import numpy as np
import os
import pickle
import openai
from typing import List, Dict
from sklearn.neighbors import NearestNeighbors
from pathlib import Path


class VectorStore:
    def __init__(
        self, index_path: Path = None, model="text-embedding-3-small"
    ):

        self.index_path = index_path
        if self.index_path is None:
            self.index_path = Path(
                Path(__file__).parent.parent, "vector_store"
            )

        self.model = model
        self.vectors = np.array([]).reshape(0, 1536)  # 1536 dims for text-embedding-3-small
        self.metadata = []
        self.nn = NearestNeighbors(n_neighbors=5, metric='euclidean')

        # Load existing index if available
        self._load()

    def get_embedding(self, text: str) -> List[float]:
        try:
            response = openai.embeddings.create(input=[text], model=self.model)
            embedding = response.data[0].embedding
            if len(embedding) != 1536:
                raise ValueError("Unexpected embedding size.")
            return embedding
        except Exception as e:
            print(f"❌ Failed to embed: {text[:60]}... — {e}")
            return []

    def add_documents(self, docs: List[Dict]):
        vectors = []
        clean_metadata = []

        for doc in docs:
            emb = self.get_embedding(doc["summary_processed"])

            if len(emb) != 1536:
                print(
                    f"⚠️ Skipping invalid embedding for: {doc.get('title', 'Unknown')}"
                )
                continue

            vectors.append(emb)
            clean_metadata.append(doc)

        if vectors:
            vectors_np = np.array(vectors).astype("float32")
            
            # Add to existing vectors
            if len(self.vectors) == 0:
                self.vectors = vectors_np
            else:
                self.vectors = np.vstack([self.vectors, vectors_np])
            
            self.metadata.extend(clean_metadata)
            
            # Retrain the nearest neighbors model
            if len(self.vectors) > 0:
                self.nn.fit(self.vectors)
            
            self._save()
            print(
                f"✅ Added {len(clean_metadata)} valid documents to the vector index."
            )
        else:
            print("❌ No valid embeddings to add.")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if len(self.vectors) == 0:
            return []
        
        q_vector = np.array([self.get_embedding(query)]).astype("float32")
        distances, indices = self.nn.kneighbors(q_vector, n_neighbors=min(top_k, len(self.vectors)))
        return [self.metadata[i] for i in indices[0]]

    def _save(self):
        if not self.index_path.exists():
            self.index_path.mkdir(parents=True)

        # Save vectors as numpy array
        np.save(Path(self.index_path, "vectors.npy"), self.vectors)

        with open(Path(self.index_path, "metadata.pkl"), "wb") as f:
            pickle.dump(self.metadata, f)

    def _load(self):
        try:
            vectors_file = Path(self.index_path, "vectors.npy")
            metadata_file = Path(self.index_path, "metadata.pkl")

            if vectors_file.exists() and metadata_file.exists():
                self.vectors = np.load(vectors_file)
                
                # Validate that loaded vectors match expected dimension
                if self.vectors.shape[1] != 1536:
                    print(
                        f"⚠️ Dimension mismatch: expected 1536, got {self.vectors.shape[1]}"
                    )
                    print("🧹 Clearing saved index to match new model.")
                    os.remove(vectors_file)
                    os.remove(metadata_file)
                    return  # Leave self.vectors as newly initialized
                else:
                    with open(metadata_file, "rb") as f:
                        self.metadata = pickle.load(f)
                    
                    # Fit the nearest neighbors model
                    if len(self.vectors) > 0:
                        self.nn.fit(self.vectors)
                    
                    print(
                        f"📦 Loaded vector index with {len(self.metadata)} items."
                    )
        except Exception as e:
            print(f"⚠️ Could not load existing vector index: {e}")
