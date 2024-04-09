import os
from dataclasses import dataclass
import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Connect to the database
con = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = con.cursor()

# Ensure the table exists
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS prompts (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        prompt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        favorite BOOLEAN DEFAULT FALSE
    )
    """
)

@dataclass
class Prompt:
    title: str
    prompt: str

def prompt_form(prompt=Prompt("", "")):
    """
    Form for creating or editing prompts. Includes validation.
    """
    with st.form(key="prompt_form", clear_on_submit=True):
        title = st.text_input("Title", value=prompt.title)
        prompt_text = st.text_area("Prompt", height=200, value=prompt.prompt)
        submitted = st.form_submit_button("Submit")
        if submitted and title and prompt_text:
            return Prompt(title, prompt_text)
        elif submitted:
            st.error("Both title and prompt are required.")

st.title("Promptbase")
st.subheader("A simple app to store and retrieve prompts")

# Add a search bar
search_query = st.text_input('Search prompts')
sort_order = st.selectbox("Sort by", ["Newest first", "Oldest first"])

# Add prompt
prompt = prompt_form()
if prompt:
    cur.execute("INSERT INTO prompts (title, prompt) VALUES (%s, %s)", (prompt.title, prompt.prompt,))
    con.commit()
    st.success("Prompt added successfully!")

# Search and sort prompts
if search_query:
    cur.execute("SELECT * FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s ORDER BY created_at DESC" if sort_order == "Newest first" else "SELECT * FROM prompts WHERE title ILIKE %s OR prompt ILIKE %s ORDER BY created_at", (f'%{search_query}%', f'%{search_query}%'))
else:
    cur.execute("SELECT * FROM prompts ORDER BY created_at DESC" if sort_order == "Newest first" else "SELECT * FROM prompts ORDER BY created_at")

prompts = cur.fetchall()

for p in prompts:
    with st.expander(f"{p[1]} ({'Favorite' if p[5] else 'Not Favorite'})"):
        st.code(p[2])
        # Toggle favorite status
        if st.button("Toggle Favorite", key=f"fav_{p[0]}"):
            cur.execute("UPDATE prompts SET favorite = NOT favorite WHERE id = %s", (p[0],))
            con.commit()
            st.rerun()
        # Delete functionality
        if st.button("Delete", key=p[0]):
            cur.execute("DELETE FROM prompts WHERE id = %s", (p[0],))
            con.commit()
            st.experimental_rerun()

# Note: Edit functionality requires a more detailed implementation for UI state management
