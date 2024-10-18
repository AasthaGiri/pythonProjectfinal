from flask import Flask, request, render_template
import os
import re

app = Flask(__name__)

# Paths to your document and query files
DOCUMENT_PATH = r"C:\Users\giria\Desktop\CISI.ALL"
QUERY_PATH = r"C:\Users\giria\Desktop\tech400\query.txt"


# Function to load and preprocess the documents
def load_documents():
    documents = {}
    for filename in os.listdir(DOCUMENT_PATH):
        file_path = os.path.join(DOCUMENT_PATH, filename)
        if os.path.isfile(file_path):  # Ensure it's a file
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                documents[filename] = content.strip()  # Use filename as the document ID
    return documents


# Function to load and preprocess the queries
def load_queries():
    queries = {}
    with open(QUERY_PATH, 'r', encoding='utf-8') as file:
        content = file.read()
        raw_queries = content.split(".I ")
        for raw_query in raw_queries[1:]:
            query_id, query_text = raw_query.split("\n", 1)
            queries[int(query_id.strip())] = query_text.strip()
    return queries


# Preprocess text (documents and queries) by tokenizing and normalizing
def preprocess(text):
    return re.findall(r'\w+', text.lower())


# Create inverted index from documents
def create_inverted_index(documents):
    inverted_index = {}
    for doc_id, text in documents.items():
        words = preprocess(text)
        for word in words:
            if word not in inverted_index:
                inverted_index[word] = set()
            inverted_index[word].add(doc_id)
    return inverted_index


# Boolean search function
def boolean_search(query):
    tokens = preprocess(query)
    results = None

    if 'and' in tokens:
        sets = [inverted_index.get(token, set()) for token in tokens if token != 'and']
        results = set.intersection(*sets) if sets else set()
    elif 'or' in tokens:
        sets = [inverted_index.get(token, set()) for token in tokens if token != 'or']
        results = set.union(*sets) if sets else set()
    elif 'not' in tokens:
        not_index = tokens.index('not')
        positive_term = inverted_index.get(tokens[not_index - 1], set())
        negative_term = inverted_index.get(tokens[not_index + 1], set())
        results = positive_term - negative_term
    else:
        results = inverted_index.get(tokens[0], set())

    return results


# Load documents and create inverted index at startup
documents = load_documents()
inverted_index = create_inverted_index(documents)
queries = load_queries()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']  # Accept string input
    result_ids = boolean_search(query)

    results = []
    if result_ids:
        for doc_id in result_ids:
            results.append((doc_id, documents[doc_id]))  # Include document name and content
    return render_template('results.html', query=query, results=results)


if __name__ == "__main__":
    app.run(debug=True)
