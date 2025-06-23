import faiss
import numpy as np
import os
import pickle
import openai
from typing import List, Dict

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
        self.index = faiss.IndexFlatL2(
            1536
        )  # 1536 dims for text-embedding-3-small
        self.metadata = []

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

            if len(emb) != self.index.d:
                print(
                    f"⚠️ Skipping invalid embedding for: {doc.get('title', 'Unknown')}"
                )
                continue

            vectors.append(emb)
            clean_metadata.append(doc)

        if vectors:
            vectors_np = np.array(vectors).astype("float32")
            self.index.add(vectors_np)
            self.metadata.extend(clean_metadata)
            self._save()
            print(
                f"✅ Added {len(clean_metadata)} valid documents to the vector index."
            )
        else:
            print("❌ No valid embeddings to add.")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        q_vector = np.array([self.get_embedding(query)]).astype("float32")
        distances, indices = self.index.search(q_vector, top_k)
        return [self.metadata[i] for i in indices[0]]

    def _save(self):

        if not self.index_path.exists():
            self.index_path.mkdir(parents=True)

        faiss.write_index(
            self.index, os.path.join(self.index_path, "index.faiss")
        )

        with open(Path(self.index_path, "metadata.pkl"), "wb") as f:
            pickle.dump(self.metadata, f)

    def _load(self):
        try:
            index_file = Path(self.index_path, "index.faiss")
            metadata_file = Path(self.index_path, "metadata.pkl")

            if index_file.exists() and metadata_file.exists():

                loaded_index = faiss.read_index(str(index_file.absolute()))

                # Validate that loaded index matches expected dimension
                if loaded_index.d != self.index.d:
                    print(
                        f"⚠️ Dimension mismatch: expected {self.index.d}, got {loaded_index.d}"
                    )
                    print("🧹 Clearing saved index to match new model.")
                    os.remove(index_file)
                    os.remove(metadata_file)
                    return  # Leave self.index as newly initialized
                else:
                    self.index = loaded_index
                    with open(metadata_file, "rb") as f:
                        self.metadata = pickle.load(f)
                    print(
                        f"📦 Loaded vector index with {len(self.metadata)} items."
                    )
        except Exception as e:
            print(f"⚠️ Could not load existing vector index: {e}")
