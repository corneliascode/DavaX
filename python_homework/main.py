import streamlit as st
import base64
import asyncio
from math_utils import compute_power, compute_fibonacci, compute_factorial
from database import AsyncSessionLocal, requests_log
from sqlalchemy import insert


######################################################
        # Design for the Streamlit app #
######################################################


# convert an image file to a base64-encoded string for inline usage in CSS
def get_img_as_base64(file_path):
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img = get_img_as_base64("photo.jpg")

# Inline CSS to style the main app background and sidebar with custom images and overlay
st.set_page_config(page_title="Math Operations", layout="centered")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("https://images.unsplash.com/photo-1501426026826-31c667bdf23d");
    background-size: 180%;
    background-position: top left;
    background-repeat: no-repeat;
    background-attachment: local;
    background-color: rgba(255, 255, 255, 0.85);
    border-radius: 12px;
    padding: 1.5rem;
}}

[data-testid="stSidebar"] > div:first-child {{
    background-image: url("data:image/png;base64,{img}");
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
    background-attachment: fixed;
    border-radius: 0.5rem;
    position: relative;
}}

[data-testid="stSidebar"] > div:first-child::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: rgba(0, 0, 0, 0.3);
    z-index: 0;
    border-radius: 0.5rem;
}}

[data-testid="stSidebar"] * {{
    position: relative;
    z-index: 1;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
    right: 2rem;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# Synchronous wrapper around asynchronous DB logging using SQLAlchemy

def log_request_sync(operation: str, input_str: str, result_str: str):
    async def _log():
        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = insert(requests_log).values(
                    operation=operation.lower(),
                    input=input_str,
                    result=result_str
                )
                await session.execute(stmt)
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_log())
    finally:
        loop.close()


######################################################
        # UI: Sidebar + Main Form #
######################################################

# Set the page title
st.title("Math Operations")

# Sidebar for operation selection
st.sidebar.title("Operations")
operation = st.sidebar.radio("Choose one:", ["Power", "Fibonacci", "Factorial"])

# Main form for inputs
with st.form("math_form"):
    st.subheader(f"{operation} Operation")

    # Dynamically render input fields based on selected operation
    if operation == "Power":
        base = st.number_input("Enter base", value=2, min_value=0, max_value=1_000_000)
        exponent = st.number_input("Enter exponent", value=3, min_value=0, max_value=1000)
    elif operation == "Fibonacci":
        base = st.number_input("Enter position (n)", value=10, min_value=0, max_value=100_000)
    elif operation == "Factorial":
        base = st.number_input("Enter number (n)", value=5, min_value=0, max_value=5000)

    # Option to log the request
    log_it = st.checkbox("Log to database", value=True)

    # Submit button to trigger computation
    submitted = st.form_submit_button("Compute")


######################################################
        # UI: Computation Logic #
######################################################


# Perform computation and logging if the form is submitted
if submitted:
    try:
        # Select the appropriate operation and compute the result
        if operation == "Power":
            result = compute_power(int(base), int(exponent))
            input_str = f"{int(base)}^{int(exponent)}"
        elif operation == "Fibonacci":
            result = compute_fibonacci(int(base))
            input_str = f"fib({int(base)})"
        elif operation == "Factorial":
            result = compute_factorial(int(base))
            input_str = f"{int(base)}!"

        # Display the result to the user
        st.success(f"**Result**: `{result}`")

        # Log to database if the checkbox is selected
        if log_it:
            log_request_sync(operation, input_str, str(result))
            st.info("Logged to database successfully.")

    # Catch and display any exceptions
    except Exception as e:
        st.error(f"Error: {str(e)}")
