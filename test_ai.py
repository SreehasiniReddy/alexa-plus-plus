
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the API key from your local .env file
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("API key not found. Check your .env file.")
else:
    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input="You are Alexa++, a friendly personal assistant. Introduce yourself in one short sentence."
        )

        print("\n✨ Alexa++ AI is connected!")
        print(response.output_text)

    except Exception as error:
        print("\nAI connection failed.")
        print("Error:", str(error))
