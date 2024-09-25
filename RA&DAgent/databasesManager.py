from statusDatabaseManager import StatusEnum, StatusDatabaseManager

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import filter_complex_metadata

import os


class DatabasesManager:

    def __init__(self): 
        self.route = os.path.join(os.getcwd(), "RA&DAgent" ,"databases")
        self.embedding_model = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-mpnet-base-v2")
        self.status_database = StatusDatabaseManager()
        

    def create_database(self, container_path:str, database_name:str):
        """
            Creates a new database from the provided container path and saves embeddings.

            This method initializes a new database by preparing data from the specified container path and saving
            the embeddings to a directory named after the provided `database_name`. It performs several checks
            to ensure the database is not created if the folder does not exist or if a database with the same name
            already exists.

            - The method first checks if the specified container path exists. If not, it raises a `ValueError`.
            - It then checks if a directory with the provided database name already exists in the base route. If so,
            it raises a `ValueError`.
            - If the checks pass, it prepares the data by calling `_prepare_data`, which processes the documents
            from the container path.
            - After preparing the data, it saves the embeddings to a new directory named after `database_name` using
            `_save_embeddings`.

            Args:
                container_path (str): The path to the directory containing the documents to be processed.
                database_name (str): The name of the database to be created, which also determines the directory
                                    where embeddings will be stored.

            Raises:
                ValueError: If the container path does not exist or if a database with the same name already exists.
        """
            
        if (not (os.path.exists(container_path))): 
            raise ValueError("Folder does not exist")
        
        files = os.listdir(self.route)
        if database_name in files: 
            raise ValueError("Database already exists")
                
        database_path = os.path.join(self.route, database_name)
        
        split_documents = self._prepare_data(container_path)
        
        '''
        for doc in split_documents:
            print(f"File: {doc.metadata['file']}, Página: {doc.metadata['page_number']}, Chunk: {doc.page_content[:100]}...")
        '''
        ##Synchronous wait 
        self._save_embeddings(database_name=database_name, split_documents=split_documents)
        '''
        docs = self.retrieval_augmented(database_name=database_name,query_text="Se usa unity o unreal engine y para que? ")
   
        for doc in docs:
            print(doc.page_content)
            print()
        '''
          
        
    def _prepare_data(self, container_path): 
        """
        Loads PDF documents from the specified directory, splits the content of each page into smaller chunks,
        and organizes them into a list of `Document` objects with metadata.

        This method scans the given directory for PDF files, loads each PDF file using the `PyPDFLoader`,
        and splits the content of each page into smaller chunks using the `RecursiveCharacterTextSplitter`.
        Each chunk is stored in a `Document` object, which contains both the chunked text and relevant metadata
        such as the file name and page number. The final structure is a list where each element corresponds 
        to a chunk of text from a specific page in a PDF document.

        - Each `Document` object contains the chunked text as well as metadata with the file name and page number.

        Args:
            container_path (str): The path to the directory containing the PDF files.

        Returns:
            List[Document]: A list of `Document` objects, where each object represents a chunk of text from a specific 
                            page of a PDF document. Each `Document` object contains:
                            - `page_content` (str): The chunk of text extracted from the page.
                            - `metadata` (dict): Metadata about the chunk, including:
                                - "file" (str): The name of the PDF file.
                                - "page_number" (int): The page number from which the chunk is extracted.

        Notes:
            - For large PDF files or a large number of PDF files, consider using a lazy loader to avoid 
            excessive memory usage. With a lazy loader, the PDF content is loaded incrementally and processed
            in chunks.
            
            - The content of each page is split into smaller chunks using `RecursiveCharacterTextSplitter`, 
            which allows control over the size of the chunks and overlap between them. The chunk size 
            and overlap are based on the text splitter's configuration, not the page size.
    """

        files = os.listdir(container_path)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " "]  
        )
        split_documents = []


        for file in files:
            path = os.path.join(container_path, file)
            loader = PyPDFLoader(path)
            documents = loader.load()
        
            for page_number, document in enumerate(documents, start=1): 
                chunks = text_splitter.split_text(document.page_content) 
                for chunk in chunks:
                    split_documents.append(
                        Document(
                            page_content=chunk,
                            metadata={         
                                "file": os.path.basename(path),
                                "page_number": page_number  
                            }
                        )
                    )

        return split_documents
    
    
    def _save_embeddings(self, database_name, split_documents):
        """
        Saves or loads embeddings for the specified database using the provided documents.

        This method manages the storage of embeddings associated with a particular database. If the
        embeddings already exist in the specified directory, they are loaded; otherwise, new embeddings
        are created from the provided documents and saved to the directory.

        - The method checks if the directory for storing embeddings already exists.
        - If the directory exists, it loads the embeddings from this directory using `Chroma`.
        - If the directory does not exist, it creates a new embeddings store from the provided documents
        using `Chroma.from_documents`, then saves it to the specified path.

        Args:
            database_name (str): The name of the database, which is used to determine the directory path
                                for storing the embeddings.
            split_documents (List[Document]): A list of documents to be used for creating embeddings.
                                            The documents should be pre-processed and split as needed.
    """
        
        path =  os.path.join(self.route, database_name)
        vector_store = path
               
        if os.path.exists(vector_store):
            vector_store_loaded = Chroma(persist_directory=vector_store, embedding_function=self.embedding_model)
        else:
            vector_store = Chroma.from_documents(
                documents=filter_complex_metadata(split_documents),
                embedding=self.embedding_model,
                persist_directory = path
            )
            self.status_database.update_entry_status(database_id=database_name, new_status=StatusEnum.ready)

            
    def retrieval_augmented(self, database_name: str, query_text: str, top_k: int = 5, similarity_threshold: float = 0.7):
        """
        Performs retrieval-augmented search on the specified database using the provided query text.

        This method retrieves documents from a database based on a query text. It uses an existing embeddings
        store to perform the search and return relevant documents based on similarity.

        - The method initializes the `Chroma` retriever with embeddings stored in the specified directory.
        - It then creates a retriever object configured to use "mmr" (Maximum Marginal Relevance) for the search,
        with the number of top documents to retrieve specified by `top_k`.
        - The retriever is used to find and return documents that are relevant to the provided query text.

        Args:
            database_name (str): The name of the database to retrieve embeddings from.
            query_text (str): The text of the query used to search for relevant documents.
            top_k (int, optional): The number of top documents to retrieve. Defaults to 5.
            similarity_threshold (float, optional): The minimum similarity score required for documents to be
                                                    considered relevant. Defaults to 0.7.

        Returns:
            List[Document]: A list of retrieved documents that match the query text, ordered by relevance.
    """
        
        
        path = os.path.join(self.route, database_name)    
        
        vector_store_loaded = Chroma(persist_directory=path, embedding_function=self.embedding_model)
        
        retriever = vector_store_loaded.as_retriever(search_type="mmr", search_kwargs={"k": top_k})
        
        retrieved_docs = retriever.invoke(query_text)
        
        return retrieved_docs

        
        