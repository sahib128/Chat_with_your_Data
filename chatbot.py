import json
import numpy as np
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def query_rag(query_text: str, embedding_path):
    # Load embeddings from JSON file
    embeddings_file_path =embedding_path
    with open(embeddings_file_path, 'r') as f:
        embeddings = json.load(f)

    # Get the dictionary from the list
    embeddings_dict = embeddings[0]

    # Get the chunk text and embedding
    chunk_text = embeddings_dict['chunk']
    chunk_embedding = np.array(embeddings_dict['embedding'])

    # Create prompt and get response from model
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=chunk_text, question=query_text)
    model = Ollama(model="llama3.1")
    response_text = model.invoke(prompt)

    return response_text


def main():
    while True:
        query_text = input("Enter your query (or 'exit' to quit): ")
        if query_text.lower() == 'exit':
            break
        response = query_rag(query_text,"embeddings/crime-drop-in-america.pdf_embeddings.json")
        print(response)


if __name__ == "__main__":
    main()
