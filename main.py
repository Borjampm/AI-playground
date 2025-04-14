import tkinter as tk
from tkinter import scrolledtext, messagebox, TclError
import google.generativeai as genai
import os
from dotenv import load_dotenv
import threading

load_dotenv() # Load environment variables from .env file

# --- Gemini Initialization ---
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")

    genai.configure(api_key=api_key)
    # Initialize the generative model
    model = genai.GenerativeModel('gemini-1.5-flash-latest') # Use a known valid model
    print("Successfully connected to Google Gemini API.")

except ValueError as ve:
    # Use messagebox for GUI errors before root window exists
    root_temp = tk.Tk()
    root_temp.withdraw() # Hide the temporary root window
    messagebox.showerror("Configuration Error", f"Configuration Error: {ve}")
    root_temp.destroy()
    exit() # Exit if API key is missing
except Exception as e:
    root_temp = tk.Tk()
    root_temp.withdraw()
    messagebox.showerror("Initialization Error", f"An error occurred during initialization: {e}")
    root_temp.destroy()
    exit() # Exit on other init errors

# --- GUI Functions ---
def send_message(event=None): # Added event=None for binding
    user_input = input_entry.get("1.0", tk.END).strip()
    if not user_input:
        return # Do nothing if input is empty

    # Disable input and button while processing
    input_entry.config(state=tk.DISABLED)
    send_button.config(state=tk.DISABLED)
    conversation_area.config(state=tk.NORMAL)
    conversation_area.insert(tk.END, f"You: {user_input}\n\n")
    conversation_area.config(state=tk.DISABLED)
    input_entry.delete("1.0", tk.END) # Clear input field

    # Run Gemini call in a separate thread to avoid blocking the GUI
    threading.Thread(target=get_gemini_response, args=(user_input,), daemon=True).start()

def get_gemini_response(user_input):
    thinking_message = "Gemini: Thinking...\n\n"
    try:
        conversation_area.config(state=tk.NORMAL)
        conversation_area.insert(tk.END, thinking_message)
        conversation_area.see(tk.END) # Scroll to the bottom
        conversation_area.config(state=tk.DISABLED)

        response = model.generate_content(user_input)

        conversation_area.config(state=tk.NORMAL)
        # Delete "Thinking..." message more robustly
        try:
            # Calculate start/end index based on the length of the thinking message
            num_lines_thinking = thinking_message.count('\n')
            start_index = f"end-{num_lines_thinking+1}l linestart" # Go back number of lines + 1
            end_index = f"end-{num_lines_thinking}l linestart"     # End before the last line break
            # A simpler way: delete the last few characters equal to the length of thinking_message
            start_del_index = f"end - {len(thinking_message)} chars"
            conversation_area.delete(start_del_index, tk.END)
        except TclError:
            print("Error deleting thinking message") # Log error if needed
            pass # Ignore if deletion fails

        conversation_area.insert(tk.END, f"Gemini: {response.text}\n\n")
        conversation_area.see(tk.END) # Scroll to the bottom

    except Exception as e:
        conversation_area.config(state=tk.NORMAL)
        # Attempt to delete "Thinking..." even if error occurred
        try:
            start_del_index = f"end - {len(thinking_message)} chars"
            actual_content = conversation_area.get(start_del_index, tk.END)
            if actual_content.strip() == thinking_message.strip(): # Check if it's actually the thinking message
                 conversation_area.delete(start_del_index, tk.END)
        except TclError:
            print("Error deleting thinking message after exception")
            pass # Ignore if deletion fails

        conversation_area.insert(tk.END, f"Gemini: Error - {e}\n\n")
    finally:
        # Ensure state is disabled before re-enabling input
        try:
             conversation_area.config(state=tk.DISABLED)
        except TclError: # Window might be destroyed
            pass
        # Re-enable input and button on the main thread
        if root.winfo_exists(): # Check if window still exists
             root.after(0, enable_input)

def enable_input():
    try:
        if root.winfo_exists():
            input_entry.config(state=tk.NORMAL)
            send_button.config(state=tk.NORMAL)
            input_entry.focus_set() # Set focus back to input
    except TclError:
        pass # Ignore if widgets are already destroyed

# --- GUI Setup ---
root = tk.Tk()
root.title("Gemini Chat")
root.geometry("600x500") # Set a default size

# Configure grid layout
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Conversation display area
conversation_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, height=20, width=60)
conversation_area.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

# Input text area (using Text for multi-line)
input_entry = tk.Text(root, height=3)
input_entry.grid(row=1, column=0, pady=(0,10), padx=(10,0), sticky="nsew")
# Bind Enter to send_message, allow Shift+Enter for newline
input_entry.bind("<KeyPress-Return>", lambda event: send_message() if not event.state & 1 else None)
input_entry.bind("<Shift-KeyPress-Return>", lambda event: input_entry.insert(tk.INSERT, '\n'))

# Send button
send_button = tk.Button(root, text="Send", command=send_message)
send_button.grid(row=1, column=1, pady=(0,10), padx=(0,10), sticky="nsew")
root.grid_columnconfigure(1, weight=0) # Don't let button column expand
root.grid_rowconfigure(1, weight=0) # Don't let input row expand vertically much


# Initial focus
input_entry.focus_set()

# Start the GUI event loop
root.mainloop()

# --- Old terminal loop is removed implicitly by replacing the file content ---
