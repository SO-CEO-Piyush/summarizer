import os
import warnings
import logging
from langchain_community.document_loaders import UnstructuredFileLoader

logger = logging.getLogger(__name__)

def extract_text(file_path: str) -> str:
    logger.info(f"extracting text from: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"file not found: {file_path}")
        raise FileNotFoundError(f"file not found: {file_path}")

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            loader = UnstructuredFileLoader(file_path)
            documents = loader.load()

        if not documents:
            logger.error(f"no content extracted from: {file_path}")
            raise ValueError(f"no content extracted from: {file_path}")

        text_length = sum(len(doc.page_content) for doc in documents)
        logger.info(f"extracted {text_length} characters from {len(documents)} documents")
        return " ".join([doc.page_content for doc in documents])
    except Exception as e:
        logger.error(f"failed to extract text: {str(e)}")
        raise RuntimeError(f"failed to extract text from {file_path}: {str(e)}")
