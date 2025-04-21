from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class ReportService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model_name="gpt-4")
        self.vector_store = None
        self.initialize_vector_store()
    
    def initialize_vector_store(self):
        # Load medical cases from PDF files in the cases directory
        cases_dir = "backend/data/cases"
        if not os.path.exists(cases_dir):
            os.makedirs(cases_dir)
            return
        
        documents = []
        for file in os.listdir(cases_dir):
            if file.endswith(".pdf"):
                loader = PyPDFLoader(os.path.join(cases_dir, file))
                documents.extend(loader.load())
        
        if documents:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            texts = text_splitter.split_documents(documents)
            self.vector_store = Chroma.from_documents(
                texts,
                self.embeddings,
                collection_name="medical_cases"
            )
    
    async def generate_report(self, conversation_summary: str) -> Optional[str]:
        if not self.vector_store:
            return "No medical cases available for reference."
        
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever()
            )
            
            prompt = f"""
            Based on the following conversation summary and similar medical cases, 
            generate a comprehensive medical report. Include:
            1. Patient's condition and symptoms
            2. Relevant medical history
            3. Potential diagnoses
            4. Recommended treatments
            5. Follow-up recommendations
            
            Conversation Summary:
            {conversation_summary}
            """
            
            response = qa_chain.run(prompt)
            return response
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            return None 