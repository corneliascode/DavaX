###############################################################################
# Streamlit UI
###############################################################################

##################################################################
# 1) Imports and light configuration
##################################################################
import streamlit as st                                
from finding_books import (                            
    get_final_summary, generate_fictional_book, search_books
)

##################################################################
# Basic page setup (title, layout, header)
##################################################################
# Page metadata + layout (center content for a compact feel)
st.set_page_config(page_title="AI Book Finder", layout="centered")

# App title (HTML to center)
st.markdown("<h1 style='text-align: center;'>Smart Librarian</h1>", unsafe_allow_html=True)
st.markdown("---")

##################################################################
# Cache wrappers to avoid recomputing identical requests
##################################################################
@st.cache_data
def cached_get_final_summary(title: str) -> str:
    """
    Input : book title
    Effect: memoize summary generation for the same title
    Note  : use ttl=... or show_spinner=False in decorators if you need variants
    """
    return get_final_summary(title)

@st.cache_data
def cached_generate_fictional_book(query: str) -> tuple:
    """
    Input : user query string
    Output: (generated_title, generated_summary)
    Note  : cached per unique query; change query to force recompute
    """
    return generate_fictional_book(query)

##################################################################
# User input: free-text search box
##################################################################
# Prompt user for the kind of story; returns "" until typed
user_input = st.text_input(
    "What kind of story are you looking for?",
    placeholder="e.g. Something about rebellion and freedom"
)

##################################################################
# Action flow: on click, search and render results
##################################################################
# Button triggers a rerun; branch logic lives inside
if st.button("Recommend Books"):
    # minimal validation — ensure non-empty, trimmed text
    if user_input.strip():
        # search existing corpus (semantic/keyword per your implementation)
        with st.spinner("Searching the library..."):
            matches = search_books(user_input)

        # if matches exist -> list them with a short summary
        if matches:
            st.success(f"Found {len(matches)} relevant books:")

            # render each match with an expandable summary
            for i, title in enumerate(matches, start=1):
                # 5e-i: show a compact header per result
                st.markdown(f"### {i}. **{title}**")

                # lazy-load summary on expand, with a spinner for UX
                with st.expander("View Summary"):
                    with st.spinner(f"Generating summary for {title}..."):
                        summary = cached_get_final_summary(title)
                    st.markdown(summary)  # summaries may contain Markdown

                # visual separator between summaries
                st.markdown("---")

        # if no matches synthesize a personalized recommendation
        else:
            st.info("No matches found. Here's a personalized book recommendation:")

            # generate (title, summary) from the user's query
            with st.spinner("Creating a personalized book recommendation..."):
                fictional_title, fictional_summary = cached_generate_fictional_book(user_input)

            # present the generated recommendation (open by default)
            st.markdown("### **Generated Recommendation**")
            st.markdown(f"**{fictional_title}**")
            with st.expander("View Summary", expanded=True):
                st.markdown(fictional_summary)

            # separator after the recommendation
            st.markdown("---")

    # empty input: prompt user to type something
    else:
        st.warning("Please enter a description or keywords to search.")
