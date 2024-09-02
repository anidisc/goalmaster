#claasse principale funzione gemini ai
import google.generativeai as genai
#from google.colab import userdata

#GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')
GOOGLE_API_KEY="AIzaSyCT1v4ys_X91owPyOmtVQqfKHjl5GN4p0Y"
genai.configure(api_key=GOOGLE_API_KEY)


def gemini_ai_call(prompt):

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

print(gemini_ai_call("come si gioca a tris"))


