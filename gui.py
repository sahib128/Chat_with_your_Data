import customtkinter
import os
import threading
import json
from tkinter import filedialog
from saveEmbeddings import process_pdf  # Ensure this function is correctly imported
from chatbot import query_rag  # Ensure this function is correctly imported

# Set appearance mode and theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Initialize main window
root = customtkinter.CTk()
root.geometry("800x500")  # Increase the size of the window
root.title("PDF Embeddings Chat")

# Create the main frame
frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# Define a font for better readability
custom_font = customtkinter.CTkFont(family="Helvetica", size=12)
bold_font = customtkinter.CTkFont(family="Helvetica", size=12, weight="bold")

# Define frames for different sections
embeddings_frame = customtkinter.CTkFrame(master=frame)
menu_frame = customtkinter.CTkFrame(master=frame)  # Main menu frame
chat_frame = customtkinter.CTkFrame(master=frame)  # Chat frame

def show_embeddings_frame():
    menu_frame.grid_forget()
    chat_frame.grid_forget()
    embeddings_frame.grid(row=0, column=0, sticky='nsew')

def show_chat_frame():
    embeddings_frame.grid_forget()
    menu_frame.grid_forget()
    chat_frame.grid(row=0, column=0, sticky='nsew')

def show_main_menu():
    embeddings_frame.grid_forget()
    chat_frame.grid_forget()
    menu_frame.grid(row=0, column=0, sticky='nsew')

# Main Menu Buttons
embeddings_button = customtkinter.CTkButton(
    master=menu_frame,
    text="Generate Embeddings",
    command=show_embeddings_frame,
    font=custom_font
)
embeddings_button.pack(pady=20)

chat_button = customtkinter.CTkButton(
    master=menu_frame,
    text="Chat with Data",
    command=show_chat_frame,
    font=custom_font
)
chat_button.pack(pady=20)

# ------------------
# Embeddings Frame UI
# ------------------
pdf_entry = customtkinter.CTkEntry(
    master=embeddings_frame,
    placeholder_text="Enter PDF file path",
    font=custom_font
)
pdf_entry.grid(row=0, column=0, columnspan=2, pady=12, padx=10, sticky='ew')

def browse_pdf():
    pdf_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf")],
        title="Select PDF File"
    )
    pdf_entry.delete(0, customtkinter.END)
    pdf_entry.insert(0, pdf_path)

browse_button = customtkinter.CTkButton(
    master=embeddings_frame,
    text="Browse PDF",
    command=browse_pdf,
    font=custom_font
)
browse_button.grid(row=2, column=0, pady=12, padx=(10, 5), sticky='w')

# Store the embeddings in-memory for dynamic querying
embeddings_file_name = None
embeddings_file_path = None
embeddings_data = {}

def generate_embeddings():
    global embeddings_file_name, embeddings_file_path
    pdf_path = pdf_entry.get().strip()
    if not pdf_path:
        update_result("Error: Please enter or select a PDF file.")
        return

    if not os.path.exists(pdf_path):
        update_result("Error: The selected file does not exist.")
        return

    def process_and_update():
        global embeddings_file_name, embeddings_file_path
        try:
            update_result("Processing the PDF and generating embeddings...")
            messages, file_name = process_pdf(pdf_path)  # Call the function from the external file

            # Construct the full path to the embeddings file
            embeddings_file_name = file_name
            embeddings_file_path = os.path.join('embeddings/', embeddings_file_name)
            
            for message in messages:
                update_result(message)

            if embeddings_file_name:
                if os.path.exists(embeddings_file_path):
                    with open(embeddings_file_path, 'r') as file:
                        global embeddings_data
                        embeddings_data = json.load(file)
                else:
                    update_result(f"Error: Embeddings file not found at {embeddings_file_path}.")
                
                # Automatically switch to chat frame after processing
                show_chat_frame()

        except Exception as e:
            update_result(f"Error: {e}")

    threading.Thread(target=process_and_update, daemon=True).start()

generate_button = customtkinter.CTkButton(
    master=embeddings_frame,
    text="Generate Embeddings",
    command=generate_embeddings,
    font=custom_font,
    fg_color="red",  # Set the color of the button
    hover_color="darkred"
)
generate_button.grid(row=2, column=1, pady=12, padx=(5, 10), sticky='e')

result_textbox = customtkinter.CTkTextbox(
    master=embeddings_frame,
    width=750,
    height=200,
    wrap='word',
    state='disabled',
    font=custom_font
)
result_textbox.grid(row=3, column=0, columnspan=2, pady=12, padx=10, sticky='nsew')

def update_result(message):
    result_textbox.configure(state='normal')
    result_textbox.insert('end', message + '\n')
    result_textbox.configure(state='disabled')
    result_textbox.yview('end')

# Back Button for Embeddings Frame
back_button_embeddings = customtkinter.CTkButton(
    master=embeddings_frame,
    text="Back to Main Menu",
    command=show_main_menu,
    font=custom_font,
    fg_color="blue",  # Set the color of the button
    hover_color="darkblue"
)
back_button_embeddings.grid(row=4, column=0, pady=12, padx=10, sticky='sw')

# ------------------
# Chat Frame UI
# ------------------
query_entry = customtkinter.CTkEntry(
    master=chat_frame,
    placeholder_text="Enter your query",
    font=custom_font
)
query_entry.grid(row=0, column=0, pady=12, padx=10, sticky='ew')

def send_query():
    query_text = query_entry.get().strip()

    if not query_text:
        update_chat_result("Error: Please enter a query.")
        return

    if not embeddings_file_path:
        update_chat_result("Error: No embeddings file available. Please generate embeddings first.")
        return

    def handle_query():
        try:
            # Use the embeddings file path to query the chatbot
            response = query_rag(query_text, embeddings_file_path)
            update_chat_result(f"Chatbot response:\n{response}")
        except Exception as e:
            update_chat_result(f"Error: {e}")

    threading.Thread(target=handle_query, daemon=True).start()

send_button = customtkinter.CTkButton(
    master=chat_frame,
    text="Send Query",
    command=send_query,
    font=custom_font,
    fg_color="green",  # Set the color of the button
    hover_color="darkgreen"
)
send_button.grid(row=0, column=1, pady=12, padx=10, sticky='e')

chat_result_textbox = customtkinter.CTkTextbox(
    master=chat_frame,
    width=750,
    height=350,
    wrap='word',
    state='disabled',
    font=custom_font
)
chat_result_textbox.grid(row=1, column=0, columnspan=2, pady=12, padx=10, sticky='nsew')

def update_chat_result(message):
    chat_result_textbox.configure(state='normal')
    chat_result_textbox.insert('end', message + '\n')
    chat_result_textbox.configure(state='disabled')
    chat_result_textbox.yview('end')

# Back Button for Chat Frame
back_button_chat = customtkinter.CTkButton(
    master=chat_frame,
    text="Back to Main Menu",
    command=show_main_menu,
    font=custom_font,
    fg_color="blue",  # Set the color of the button
    hover_color="darkblue"
)
back_button_chat.grid(row=2, column=0, pady=12, padx=10, sticky='sw')

# Initialize by showing the main menu
show_main_menu()

# Make sure that the grid expands properly
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

# Run the main loop
root.mainloop()
