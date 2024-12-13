---

# **Plagiarism Detection System**

## **Overview**

The **Plagiarism Detection System** is a robust application designed to detect similarities between uploaded documents and stored reports using state-of-the-art machine learning techniques. It leverages **Sentence Transformers** for text embedding, **FAISS** for efficient similarity search, and **MongoDB** for embedding storage.

This project enables users to upload reports (PDF, DOCX, or TXT), generate embeddings, store them in a database, and find similarity scores for new reports, ensuring efficient and scalable detection of plagiarized content.

---

## **Features**

- **Document Parsing**: Extract text from PDFs, DOCX, and TXT files.
- **Text Embedding**: Use **Sentence Transformers** (`all-MiniLM-L6-v2`) to generate dense vector representations of text.
- **Similarity Search**: Perform high-speed similarity search using **FAISS**.
- **Database Storage**: Store embeddings and metadata in **MongoDB** for persistent access.
- **Similarity Aggregation**: Aggregate similarity scores for chunk- and report-level analysis.

---

## **Technologies Used**

- **FastAPI**: API framework for backend services.
- **Sentence Transformers**: For creating embeddings from text.
- **FAISS**: For efficient similarity search.
- **MongoDB**: For storing embeddings and metadata.
- **PyPDF2**: For extracting text from PDF files.
- **python-docx**: For extracting text from DOCX files.
- **dotenv**: For managing environment variables.

---

## **Installation**

### Prerequisites
- Python 3.8+
- MongoDB installed and running locally or on the cloud.
- Virtual environment (optional but recommended).

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/plagiarism-detection-system.git
   cd plagiarism-detection-system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add the following:
   ```env
   MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB=plagiarism_detection
   ```

4. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

---

## **Usage**

1. **Upload a Report**:
   Use the `/upload_report/` endpoint to upload a report and store its embeddings in the database.

2. **Find Similarity**:
   Use the `/find_similarity_with_upload/` endpoint to upload a new report and find similarities with stored reports.

---

## **API Documentation**

### **Base URL**
```plaintext
http://127.0.0.1:8000/
```

### **Endpoints**

#### 1. **Home**
- **URL**: `/`
- **Method**: `GET`
- **Description**: Returns a simple welcome message.
- **Response**:
  ```json
  {
    "Hello , Sandesh here just testing route 😅"
  }
  ```

---

#### 2. **Upload Report**
- **URL**: `/upload_report/`
- **Method**: `POST`
- **Description**: Upload a report to generate embeddings and store them in MongoDB.
- **Parameters**:
  - **File**: A file in `.pdf`, `.docx`, or `.txt` format.
- **Response**:
  ```json
  {
    "message": "Report 'filename.ext' processed and embeddings stored successfully."
  }
  ```

---

#### 3. **Find Similarity**
- **URL**: `/find_similarity_with_upload/`
- **Method**: `POST`
- **Description**: Upload a new report to find its similarity with stored reports.
- **Parameters**:
  - **File**: A file in `.pdf`, `.docx`, or `.txt` format.
  - **top_k**: (Optional) The number of top similar chunks to return. Default: 5.
- **Response**:
  ```json
  {
    "message": "Similarity analysis for 'filename.ext' completed.",
    "chunk_level_similarity": [
      {
        "new_chunk": "chunk_text",
        "similar_chunks": [
          {
            "report_id": "report_1",
            "chunk_id": 0,
            "distance": 0.25
          }
        ]
      }
    ],
    "report_level_similarity": [
      {
        "report_id": "report_1",
        "similarity_score": 0.95
      }
    ]
  }
  ```

---

## **Project Structure**
```plaintext
.
├── main.py              # Main FastAPI application
├── tool.py              # Core logic for embeddings and similarity
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── README.md            # Project documentation
```

---

## **Future Enhancements**
- Add support for more file types (e.g., HTML).
- Introduce user authentication and role management.
- Optimize embedding storage with vector databases like Pinecone.
- Integrate a frontend for seamless user interaction.

---
