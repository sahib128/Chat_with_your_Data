from ollama_text import split_chunks


def main():
    pdf_path = "machine.pdf"
    chunks = split_chunks(pdf_path) 
    chunks = calculate_chunk_ids(chunks)
    

def calculate_chunk_ids(chunks):
    """
    Assigns a unique ID to each chunk in the format: filename:page number:chunk number.
    """
    last_page_id = None
    current_chunk_index = 0
    total_chunks = len(chunks)  # <--- Add this line to get the total number of chunks

    print(f"Total number of chunks: {total_chunks}")  # <--- Add this line to print the total number of chunks

    for chunk in chunks:

        filename = chunk.metadata.get("filename")
        page = chunk.metadata.get("page")
        

        current_page_id = f"{filename}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the chunk metadata.
        chunk.metadata["id"] = chunk_id

        # Print the chunk ID
        print(chunk_id)
        print()  # Add an empty line for readability

          
    return chunks




if __name__ == "__main__":
    main()