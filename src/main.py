from fileinput import filename
from docling.document_converter import DocumentConverter
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from pymongo import MongoClient
import os

# Load environment variables from .env file
load_dotenv()

# # gonna be replaced by api call to ragline app backend !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# # MongoDB connection string
# MONGODB_CONNECTION_STRING = "mongodb+srv://trixy:Password123@ragline.bp8lxwu.mongodb.net/"

# # Connect to MongoDB Cloud
# try:
#     client = MongoClient(MONGODB_CONNECTION_STRING)
#     # Test the connection
#     client.admin.command('ping')
#     print("Successfully connected to MongoDB Cloud!")
#     db = client['rag-v1']  # Connect to rag-v1 database
# except Exception as e:
#     print(f"Error connecting to MongoDB: {e}")
#     client = None
#     db = None

# # query mongo db and pass in wild_animals 
# # recieve data from mongodb and use those configs

# def get_config_from_mongodb(folder_path):
#     """
#     Query MongoDB configs collection for a specific folder_path
#     Returns the config document or None if not found
#     """
#     if db is None:
#         print("MongoDB connection not available")
#         return None
    
#     try:
#         configs_collection = db['configs']
#         config = configs_collection.find_one({"folder_path": folder_path})
        
#         if config:
#             print(f"Found config for folder_path: {folder_path}")
#             return config
#         else:
#             print(f"No config found for folder_path: {folder_path}")
#             return None
#     except Exception as e:
#         print(f"Error querying MongoDB: {e}")
#         return None


def main (file_path):
    # Query MongoDB for configs based on folder_path
    # Extract the directory name from file_path (e.g., "wild_animals" from "../files/wild_animals/lion.pdf")
    # Get the parent directory name from the file path
    file_dir = os.path.dirname(file_path)
    folder_path_for_query = os.path.basename(file_dir) if file_dir else "wild_animals"  # Extract "wild_animals" from path
    config = get_config_from_mongodb(folder_path_for_query)
    
    # Use configs from MongoDB if available, otherwise use defaults
    if config:
        chunk_size = config.get('chunk_size', 400)
        chunk_overlap = config.get('chunk_overlap', 20)
        chunk_strategy = config.get('chunk_strategy', "sentence")
        namespace = config.get('namespace', None)
        index_name = config.get('index_name', 'lion')
        metadata_extraction = config.get("metadata_extraction", "default")
        print(f"Using configs from MongoDB: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}, namespace={namespace}, index_name={index_name}")
    else:
        # Default values if no config found
        chunk_size = 400
        chunk_overlap = 20
        chunk_strategy = "sentence"
        namespace = None
        index_name = "lion"
        metadata_extraction = "default"
        print("Using default configs (MongoDB config not found)")


    # Parsing doc with Docling ****************************************************
    source = file_path # document per local path or URL
    converter = DocumentConverter()
    result = converter.convert(source)
    parsed_md = result.document.export_to_markdown() #  pdf to markdown 

    
    filename_with_extension = os.path.basename(file_path)
    filename_without_extension = os.path.splitext(filename_with_extension)[0]
    md_file_path = f"../files/{folder_path_for_query}/{filename_without_extension}.md"

    # Code to create md file for parse file 
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(parsed_md )

    # Load the parse.md file
    file_md = SimpleDirectoryReader(input_files=[md_file_path]).load_data()

    # Initialize connection to Pinecone
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

    # Get or create index (text-embedding-3-small has 1536 dimensions)
    # index_name is now set from MongoDB config or default above

    # Create your index (can skip this step if your index already exists)
    try:
        pc.create_index(
            index_name,
            dimension=1536,  # text-embedding-3-small dimension
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    except Exception:
        # Index already exists, continue
        pass

    # Initialize your index
    pinecone_index = pc.Index(index_name)

    # Initialize VectorStore with namespace
    vector_store = PineconeVectorStore(
        pinecone_index=pinecone_index,
        namespace=namespace
    )

    # Create embedding model
    embed_model = OpenAIEmbedding(model="text-embedding-3-small")


    # Create ingestion pipeline with transformations
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap),  # measure by tokens
            embed_model,
        ],
        vector_store=vector_store,
    )

    # Ingest directly into vector db
    pipeline.run(documents=file_md)

# main("../files/wild_animals/lion.pdf")
main("../files/domestic_animals/cat.pdf")
# main("../files/lion.pdf")