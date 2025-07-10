import chromadb
from pathlib import Path
import uuid
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional, Union


class RagUniversal():
    def __init__(self, embedding_model: str = None):
        """
        Initialize the RAG system.

        Args:
            embedding_model: Currently ignored, using default embedding model.
        """
        if embedding_model:
            print("Warning: Customized embedding model is not supported yet. Using default embedding model.")

        self.db_path = Path(__file__).resolve().parent / "RAGmodule" / "system_DB"
        self.embedding = embedding_functions.DefaultEmbeddingFunction()
        self.client = chromadb.PersistentClient(path=str(self.db_path))

        try:
            self.collection = self.client.create_collection(
                name="Default",
                embedding_function=self.embedding,
                metadata={"hnsw:space": "cosine"}
            )
        except chromadb.errors.InternalError as e:
            print(f"Collection already exists: {e}")
            self.collection = self.client.get_collection(name="Default", embedding_function=self.embedding)
            print("Using existing Default collection")

    def split_markdown_semantic(self,file_path:str)->List[str]:
        """
        This markdown splitter works well with the real markdown file
        Split a markdown file into semantic blocks.

        Args:
            file_path (str): Path to the markdown file

        Returns:
            list: List of strings, each representing a semantic block
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        blocks = []
        current_block = ""
        in_code_block = False
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Handle code blocks as complete units
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Start of a new code block
                    if current_block.strip():
                        blocks.append(current_block.strip())
                    current_block = line + '\n'
                    in_code_block = True
                else:
                    # End of a code block
                    current_block += line + '\n'
                    blocks.append(current_block.strip())
                    current_block = ""
                    in_code_block = False
                i += 1
                continue

            if in_code_block:
                current_block += line + '\n'
                i += 1
                continue

            # Headers start new blocks
            if line.strip().startswith('#'):
                if current_block.strip():
                    blocks.append(current_block.strip())
                current_block = line + '\n'
                i += 1
                continue

            # Empty lines separate paragraphs
            if not line.strip():
                if current_block.strip():
                    blocks.append(current_block.strip())
                    current_block = ""
                i += 1
                continue

            # Handle list items
            if (line.strip().startswith(('- ', '* ', '+ ')) or
                    (line.strip() and line.strip()[0].isdigit() and '.' in line.strip()[:3])):
                # Check if we need to start a new block
                if current_block.strip() and not any(current_block.strip().endswith('\n' + prefix)
                                                     for prefix in ['- ', '* ', '+ ']) and not (
                        current_block.strip().split('\n')[-1].strip() and
                        current_block.strip().split('\n')[-1].strip()[0].isdigit() and
                        '.' in current_block.strip().split('\n')[-1].strip()[:3]):
                    blocks.append(current_block.strip())
                    current_block = ""

            # Handle blockquotes
            if line.strip().startswith('>'):
                if current_block.strip() and not current_block.strip().split('\n')[-1].startswith('>'):
                    blocks.append(current_block.strip())
                    current_block = ""

            # Add the current line to the block
            current_block += line + '\n'
            i += 1

        # Add the last block if not empty
        if current_block.strip():
            blocks.append(current_block.strip())

        return blocks
    def add(self, documents_text: List[str], collection_name: str = "Default",
            meta_datas: Optional[Union[List[Dict[str, str]], Dict[str, str]]] = None):
        """
        Add documents to a collection.

        Args:
            collection_name: Name of the collection to add documents to
            documents_text: List of document texts to add
            meta_datas: List of metadata dictionaries (one per document) or a single dictionary to apply to all
        """
        try:
            current_collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding
            )
        except ValueError as e:
            print(f"Collection not found: {e}")
            print("Using Default collection instead")
            current_collection = self.collection

        # Handle metadata properly
        if meta_datas is None:
            meta_datas = [{} for _ in documents_text]
        elif isinstance(meta_datas, dict):
            # If single dict provided, duplicate it for each document
            meta_datas = [meta_datas.copy() for _ in documents_text]

        # Generate unique IDs
        ids = [str(uuid.uuid4()) for _ in range(len(documents_text))]

        current_collection.add(
            documents=documents_text,
            metadatas=meta_datas,
            ids=ids
        )

    def retrieve(self, collection_name: str, query: str, n_results: int = 5,
                 metadata: Dict[str, str] = None):
        """
        Retrieve documents from a collection based on a query.

        Args:
            collection_name: Name of the collection to query
            query: The query text
            n_results: Number of results to return
            metadata: Filter metadata (not implemented yet)

        Returns:
            Query results from ChromaDB
        """
        try:
            current_collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding
            )
        except ValueError as e:
            print(f"Collection not found: {e}")
            print("Using Default collection instead")
            current_collection = self.collection

        # For this prototype version, metadata filtering is not implemented
        if metadata:
            print("Warning: Metadata filtering not implemented yet")

        results = current_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results["documents"]
