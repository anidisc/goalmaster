#claasse principale funzione gemini ai
import google.generativeai as genai
import os

GOOGLE_API_KEY=os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


def gemini_ai_call(prompt):

#   model = genai.GenerativeModel("gemini-1.5-flash")
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(prompt)
    return response.text

#print(gemini_ai_call("come si gioca a tris"))
``

#gemini_ai_call("come si gioca a tris")
