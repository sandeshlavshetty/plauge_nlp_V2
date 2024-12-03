from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from tool import EmbeddingManager, ReportReader
import numpy as np

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_manager = EmbeddingManager()
report_reader = ReportReader()


@app.get("/")
async def upload_ui():
    return {"Hello , Sandesh here just testing route 😅"}


@app.post("/upload_report/")
async def upload_report(file: UploadFile = File(...)):
    try:
        text = ReportReader.extract_text(file)
        chunks, embeddings = embedding_manager.process_and_embed_report(text)
        embedding_manager.store_embeddings_in_mongo(file.filename, chunks, embeddings)
        return {"message": f"Report '{file.filename}' processed and embeddings stored successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/find_similarity_with_upload/")
async def find_similarity_with_upload(file: UploadFile = File(...), top_k: int = 5):
    try:
        text = ReportReader.extract_text(file)
        if not text:
            raise ValueError("Extracted text is empty!")

        # Build vector store
        embedding_manager.build_vector_store()
        if embedding_manager.vector_store is None:
            raise ValueError("Vector store not initialized!")

        # Perform similarity search
        similarity_results = embedding_manager.find_similar(text, top_k=top_k)
        aggregated_scores = embedding_manager.aggregate_similarities(similarity_results)
        print("similarity_results :- ")
        print(type(similarity_results))
        print(similarity_results)
        print("aggregated_results :- ")
        print(type(aggregated_scores))
        print(aggregated_scores)
        
        # Convert results to JSON-serializable formats
        similarity_results_serializable = [
            {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in result.items()}
            for result in similarity_results
        ]
        aggregated_scores_serializable = float(aggregated_scores)  # Convert numpy.float32 to float

        return {
            "message": f"Similarity analysis for '{file.filename}' completed.",
            "chunk_level_similarity": similarity_results,
            "report_level_similarity": aggregated_scores,
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
