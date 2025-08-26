###############################################################################
                 # Indexing the books with FAISS #

# Generates embeddings for book summaries, builds a FAISS index, saves index & titles
###############################################################################



##################################################################
# Imports + environment loading
##################################################################
import os          # for reading environment variables
import json        # for saving the ordered list of titles
import faiss       # FAISS: fast similarity search over vectors
import numpy as np # to handle numeric arrays (embeddings)
from dotenv import load_dotenv  # to load .env into environment
import openai      # OpenAI Embeddings API client

load_dotenv()                                  
openai.api_key = os.getenv("OPENAI_API_KEY")    


##################################################################
# Load book summaries (source data)
##################################################################
# Expect a dict like: {"Title A": "summary text ...", "Title B": "summary ...", ...}
from book_summaries_dict import book_summaries_dict

# Keep a stable order; index positions must align across titles and vectors
titles = list(book_summaries_dict.keys())
texts  = list(book_summaries_dict.values())


##################################################################
# Define an embedding helper 
##################################################################
def get_embeddings(texts, model="text-embedding-ada-002"):
    """
    Input : list[str] texts- each element will get one embedding
    Output: np.ndarray float32 of shape (N, D), preserving the input order
    Notes : If your texts are very long, consider chunking before embedding
            (then average or otherwise pool the chunk vectors).
    """
    embeddings = []  # accumulate vectors here (same order as `texts`)
    for text in texts:
        # Request a single embedding from OpenAI for the given text
        response = openai.Embedding.create(input=text, model=model)
        # Extract the vector from the response
        embeddings.append(response["data"][0]["embedding"])

    # Convert to float32 (FAISS prefers float32) and return
    return np.array(embeddings, dtype="float32")


##################################################################
# Generate embeddings for all summaries
##################################################################
embeddings = get_embeddings(texts) 
print(f"Generated {len(embeddings)} embeddings with dimension {len(embeddings[0])}.")

##################################################################
# Build and populate a FAISS index
##################################################################
# Detect vector dimension from the first embedding row
dimension = len(embeddings[0])

# Add all vectors to the index (row i corresponds to titles[i])
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
print("FAISS index created and populated.")

# Write index to a file you can reload later with faiss.read_index(...)
faiss.write_index(index, "book_index.faiss")
print("Saved FAISS index to 'book_index.faiss'.")

# Save titles in the same order as embeddings (to map search results back)
with open("book_titles.json", "w", encoding="utf-8") as f:
    json.dump(titles, f, ensure_ascii=False, indent=2)  # keep accents and readable JSON
print("Saved book titles to 'book_titles.json'.")



