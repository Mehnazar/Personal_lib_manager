import streamlit as st
import json
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="📚 Personal Library Manager",
    page_icon="📖",
    layout="wide"
)

# Apply custom styling (Zinc-colored theme)
custom_css = """
<style>
    body { background-color: #1c1f26; color: #ffffff; }
    .stApp { background-color: #282c34; }
    .css-1d391kg { background-color: #3a3f4b !important; border-radius: 10px; }
    .stButton>button { background-color: #7a869a; color: white; border-radius: 8px; }
    .stTextInput>div>div>input { background-color: #50586c; color: white; }
    .stNumberInput>div>div>input { background-color: #50586c; color: white; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# File handling functions
def load_library():
    """Load library data from file if it exists"""
    filename = "library.txt"
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except Exception as e:
            st.error(f"Error loading library: {e}")
            return []
    return []

def save_library(library):
    """Save library data to file"""
    filename = "library.txt"
    try:
        with open(filename, 'w') as file:
            json.dump(library, file, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = load_library()
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'message' not in st.session_state:
    st.session_state.message = None
if 'show_edit_form' not in st.session_state:
    st.session_state.show_edit_form = False
if 'edit_book_index' not in st.session_state:
    st.session_state.edit_book_index = None

# App title and sidebar
st.title("📚 Personal Library Manager")
st.sidebar.image("https://placehold.co/600x200?text=Library+Manager", width=300)

# Functions for book operations
def add_book(title, author, year, genre, read_status, rating):
    """Add a new book to the library"""
    book = {
        "title": title,
        "author": author,
        "year": year,
        "genre": genre,
        "read": read_status,
        "rating": rating,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    st.session_state.library.append(book)
    save_library(st.session_state.library)
    st.session_state.message = "Book added successfully!"
    st.rerun()

def remove_book(index):
    """Remove a book from the library"""
    if 0 <= index < len(st.session_state.library):
        st.session_state.library.pop(index)
        save_library(st.session_state.library)
        st.session_state.message = "Book removed successfully!"
        st.rerun()

def edit_book(index, title, author, year, genre, read_status, rating):
    """Edit an existing book"""
    if 0 <= index < len(st.session_state.library):
        book = st.session_state.library[index]
        book["title"] = title
        book["author"] = author
        book["year"] = year
        book["genre"] = genre
        book["read"] = read_status
        book["rating"] = rating
        book["last_edited"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        save_library(st.session_state.library)
        st.session_state.message = "Book updated successfully!"
        st.session_state.show_edit_form = False
        st.session_state.edit_book_index = None
        st.rerun()

# Sidebar navigation
menu = st.sidebar.radio(
    "Menu",
    ["📖 View Library", "➕ Add Books", "🔍 Search Books", "📊 Statistics", "ℹ️ About"]
)

# Display success messages
if st.session_state.message:
    st.success(st.session_state.message)
    st.session_state.message = None

# View Library
if menu == "📖 View Library":
    st.header("📚 Your Library")

    if st.session_state.library:
        for i, book in enumerate(st.session_state.library):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.markdown(f"### {book['title']}")
                    st.write(f"by **{book['author']}**")
                
                with col2:
                    st.write(f"**Year:** {book['year']}")
                    st.write(f"**Genre:** {book['genre']}")
                
                with col3:
                    st.write("**Status:**")
                    st.markdown("✅ Read" if book["read"] else "📖 Unread")
                
                with col4:
                    st.write("**Rating:**")
                    stars = "⭐" * book.get("rating", 3)
                    st.markdown(stars)
                
                edit_button = st.button("✏️ Edit", key=f"edit_{i}")
                delete_button = st.button("🗑️ Delete", key=f"delete_{i}")

                if edit_button:
                    st.session_state.show_edit_form = True
                    st.session_state.edit_book_index = i
                    st.rerun()

                if delete_button:
                    remove_book(i)

                st.divider()
    else:
        st.info("Your library is empty. Add some books to get started!")

# Add Books
elif menu == "➕ Add Books":
    st.header("➕ Add a New Book")

    with st.form(key="add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=2023)
        with col2:
            genre = st.text_input("Genre")
        read_status = st.checkbox("I have read this book")
        rating = st.slider("Rate this book (1-5)", 1, 5, 3)

        submit_button = st.form_submit_button("Add Book")

        if submit_button:
            if title and author:
                add_book(title, author, year, genre, read_status, rating)
            else:
                st.error("Title and author are required fields.")

# Search Books
elif menu == "🔍 Search Books":
    st.header("🔍 Search for Books")

    search_term = st.text_input("Enter book title or author name")
    search_button = st.button("Search")

    if search_button and search_term:
        results = [book for book in st.session_state.library if search_term.lower() in book["title"].lower() or search_term.lower() in book["author"].lower()]
        if results:
            for book in results:
                st.write(f"📖 **{book['title']}** by {book['author']} ({book['year']})")
        else:
            st.info("No matching books found.")

# Statistics
elif menu == "📊 Statistics":
    st.header("📊 Library Statistics")
    st.write("Coming soon...")

# About
elif menu == "ℹ️ About":
    st.header("ℹ️ About Personal Library Manager")
    st.write("This is a simple library management system built with Streamlit.")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("© 2025 Personal Library Manager by Mehnazar Umair")
