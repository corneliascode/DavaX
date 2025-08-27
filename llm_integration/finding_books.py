###############################################################################
# Finding Books — Index + Summarization Utilities
# Goal: load FAISS index + titles, provide:
#       - get_final_summary(title): 4-paragraph summary (expand or create)
#       - generate_fictional_book(query): synth title + 4-paragraph summary
#       - search_books(query, top_k): simple keyword match in titles
###############################################################################

##################################################################
# 1) Imports and API key loading
##################################################################
import os                 
import json               
import faiss             
import openai            
from dotenv import load_dotenv  

# load environment from .env if present
load_dotenv()

client = openai.OpenAI()

# set OpenAI API key for subsequent API calls
openai.api_key = os.getenv("OPENAI_API_KEY")

##################################################################
# Load FAISS index and aligned book titles
##################################################################
# Assumption: index row i corresponds to titles[i] (saved together previously)
try:
    # read the vector index (must match embedding dim used when built)
    index = faiss.read_index("book_index.faiss")

    # load titles in the *same* order the embeddings were added
    with open("book_titles.json", "r", encoding="utf-8") as f:
        titles = json.load(f)

except (IOError, ValueError) as e:
    raise Exception(f"Error loading index or titles: {e}")

##################################################################
# Load full summaries dictionary (source for expansion)
##################################################################
# Expect: book_summaries_dict: Dict[str, str] — short summaries by title
from book_summaries_dict import book_summaries_dict

##################################################################
# Summarization: expand or create a 4-paragraph summary
##################################################################
def get_final_summary(title: str) -> str:
    """
    Input : title (str)
    Output: 4-paragraph comprehensive summary (str)
    Behavior:
      - If we have a short summary locally, expand it to four paragraphs.
      - Else, generate a fresh four-paragraph summary from scratch.
    Notes:
      - Uses ChatCompletion for clarity; keep temperature moderate for cohesion.
      - Consider updating 'model' if you migrate to newer Chat Completions models.
    """
    try:
        # choose prompt path: expand existing vs. create new
        if title in book_summaries_dict:
            # expand the known (short) summary
            original_summary = book_summaries_dict[title]
            prompt = f"""
            The following is a short summary of the book '{title}':

            {original_summary}

            Please expand this short summary into a comprehensive, four-paragraph summary. Ensure the summary includes the main plot points, key characters, major themes, and the book's significance. Use a professional and engaging tone.

            Expanded Summary:
            """
        else:
            prompt = f"""
            Write a comprehensive, four-paragraph summary of the book '{title}'. Ensure the summary covers:
            - The main plot points and story arc.
            - The key characters and their development.
            - The major themes and messages.
            - The book's historical, cultural, or literary significance.

            Summary:
            """

        # call OpenAI to produce the final summary text
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a knowledgeable librarian who writes engaging and informative book summaries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,  
            temperature=0.7  
        )

        # extract text and trim whitespace
        return response.choices[0].message.content.strip()

    # return a readable error message
    except Exception as e:
        return f"Failed to generate summary for '{title}': {str(e)}"


def generate_fictional_book(query: str) -> tuple:
    """
    Input : query (str) — user's preferences/keywords
    Output: (title, summary) where summary has four paragraphs
    Behavior:
      - Ask the model to craft a plausible book title + a four-paragraph summary.
      - Parse response using simple "Title:" and "Summary:" markers.
    """
    try:
        # instruction prompt with explicit output format
        prompt = f"""
        Based on the following user request: "{query}"

        Create a fictional book recommendation that would perfectly match this request. Please provide:
        1. A compelling and realistic book title
        2. A comprehensive four-paragraph summary

        Format your response as:
        Title: [Book Title]

        Summary:
        [Four-paragraph summary]
        """

        # call OpenAI to synthesize a recommendation
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative librarian who creates fictional book recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,  
            temperature=0.8 
        )

        # get raw content and split into lines for parsing
        content = response.choices[0].message.content.strip()
        lines = content.split('\n')

        # parse "Title:" and "Summary:" sections
        title = ""
        summary = ""
        for i, line in enumerate(lines):
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
            elif line.startswith("Summary:"):
                # everything after "Summary:" is the full multi-paragraph body
                summary = '\n'.join(lines[i+1:]).strip()
                break

        # return parsed fields (caller renders them)
        return title, summary

    # fallback to a safe default if anything goes wrong
    except Exception as e:
        return "Generated Book", f"Failed to generate fictional book: {str(e)}"

##################################################################
# Simple keyword search over titles (baseline)
##################################################################
def search_books(query, top_k=3):
    """
    Input : query (str), top_k (int)
    Output: up to top_k titles with simple keyword matches (case-insensitive)
    Method:
      - Split query into words; return titles containing ANY of those words.
    Notes:
      - This is a minimal baseline. For semantic search, query the FAISS index
        with the embedding of `query` and rank by distance/score.
    """
    # normalize user query for case-insensitive matching
    query_lower = query.lower()
    matches = []

    # keep titles that contain any query token
    for title in titles:
        if any(word in title.lower() for word in query_lower.split()):
            matches.append(title)

    # cap the results (presentation layer can format further)
    return matches[:top_k]
