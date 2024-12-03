from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import pickle
from pymongo import MongoClient
from fastapi import UploadFile
import numpy as np
from dotenv import load_dotenv
import os


# Load the .env file
load_dotenv()

def clean_text(text):
    return text.replace("\n", " ").strip().lower()


def split_text_into_chunks(text, max_chunk_size=512):
    words = text.split()
    return [' '.join(words[i:i + max_chunk_size]) for i in range(0, len(words), max_chunk_size)]


class EmbeddingManager:
    def __init__(self, model_name=os.getenv('MODEL_NAME'), mongo_uri=os.getenv('MONGO_URI'), db_name=os.getenv('MONGO_DB')):
        self.model = SentenceTransformer(model_name)
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.collection = self.db["embeddings"]
        self.vector_store = None
        self.metadata = []

    def process_and_embed_report(self, report, max_chunk_size=512):
        chunks = split_text_into_chunks(clean_text(report), max_chunk_size)
        embeddings = self.model.encode(chunks, convert_to_numpy=True)
        return chunks, embeddings

    def store_embeddings_in_mongo(self, report_id, chunks, embeddings):
        records = [
            {"report_id": report_id, "chunk_id": i, "embedding": pickle.dumps(embedding)}
            for i, embedding in enumerate(embeddings)
        ]
        self.collection.insert_many(records)

    def load_embeddings_from_mongo(self):
        embeddings, metadata = [], []
        for record in self.collection.find():
            embeddings.append(pickle.loads(record["embedding"]))
            metadata.append({"report_id": record["report_id"], "chunk_id": record["chunk_id"]})
        return np.vstack(embeddings), metadata

    def build_vector_store(self):
        embeddings, metadata = self.load_embeddings_from_mongo()
        self.metadata = metadata
        self.vector_store = faiss.IndexHNSWFlat(embeddings.shape[1], 32)
        self.vector_store.add(embeddings)

    def find_similar(self, new_report, max_chunk_size=512, top_k=5):
        new_chunks, new_embeddings = self.process_and_embed_report(new_report, max_chunk_size)
        distances, indices = self.vector_store.search(new_embeddings, top_k)
        results = []
        for i, (dist_list, idx_list) in enumerate(zip(distances, indices)):
            chunk_results = [
                {
                    "report_id": self.metadata[idx]["report_id"],
                    "chunk_id": self.metadata[idx]["chunk_id"],
                    "distance": dist,
                }
                for dist, idx in zip(dist_list, idx_list)
            ]
            results.append({"new_chunk": new_chunks[i], "similar_chunks": chunk_results})
        return results

    def aggregate_similarities(self, similarity_results):
        report_scores = {}
        for result in similarity_results:
            for similar_chunk in result["similar_chunks"]:
                report_id = similar_chunk["report_id"]
                score = 1 / (1 + similar_chunk["distance"])
                report_scores[report_id] = report_scores.get(report_id, 0) + score
        return sorted(report_scores.items(), key=lambda x: x[1], reverse=True)


class ReportReader:
    @staticmethod
    def extract_text(file: UploadFile):
        if file.filename.endswith('.pdf'):
            return ReportReader.extract_text_from_pdf(file.file)
        elif file.filename.endswith('.docx'):
            return ReportReader.extract_text_from_docx(file.file)
        elif file.filename.endswith('.txt'):
            return file.file.read().decode('utf-8')
        else:
            raise ValueError("Unsupported file type.")

    @staticmethod
    def extract_text_from_pdf(file):
        from PyPDF2 import PdfReader
        return " ".join(page.extract_text() for page in PdfReader(file).pages)

    @staticmethod
    def extract_text_from_docx(file):
        import io
        from docx import Document
        doc = Document(io.BytesIO(file.read()))
        return " ".join(paragraph.text for paragraph in doc.paragraphs)

















