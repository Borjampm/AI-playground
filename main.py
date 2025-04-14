import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")

    genai.configure(api_key=api_key)

    # Initialize the generative model (replace 'gemini-pro' if needed)
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("Successfully connected to Google Gemini API.")
    print("Type 'end conversation' to exit.") # Add exit instruction

    while True:
        # Ask for input only after successful connection
        user_input = input("\nYou: ") # Changed prompt for clarity

        if user_input.lower() == "end conversation":
            print("Ending conversation. Goodbye!")
            break # Exit the loop

        # Send message to Gemini and get response
        print("\nSending message to Gemini...")
        try:
            response = model.generate_content(user_input)
            # Print the response text
            print("\nGemini:")
            print(response.text)
        except Exception as e:
            print(f"An error occurred while getting response: {e}")
            # Optionally decide if you want to break the loop on error or continue
            # break

except ValueError as ve:
    print(f"Configuration Error: {ve}")
except Exception as e:
    print(f"An error occurred: {e}")
