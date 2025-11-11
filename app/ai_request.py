import google.generativeai as genai
from app import config
from app import log

genai.configure(api_key=config.API_KEY)

def ask_gemini(question, choices):
    prompt = f"""
                Voici une question de QCM de cybersécurité :
                Question : {question}
                Choix possibles : {choices}
                Réponds UNIQUEMENT par le texte exact de la bonne réponse.
                """

    model = genai.GenerativeModel("gemini-2.5-flash")
    log.info(prompt)
    response = model.generate_content(prompt)

    return response.text.strip()