# ==============================================================================
#  This file is part of a private project and is intended for educational use only.
#  Unauthorized copying, distribution, or modification of this file, in whole or
#  in part, without explicit written permission from the author is strictly prohibited.
#
#  DISCLAIMER:
#  This program is not intended to be used for cheating, academic dishonesty,
#  or any other unethical activities. It is provided solely for learning and
#  research purposes.
#
#  © Guillaume CANCALON – All rights reserved.
# ==============================================================================

import google.generativeai as genai
from app import config
from app import log

genai.configure(api_key=config.API_KEY)

def ask_gemini(question, choices):
    prompt = f"""
                Tu es un expert en cybersécurité avec beaucoup d'experience.
                Voici une question de QCM de cybersécurité :
                Question : {question}
                Choix possibles : {choices}
                Réponds UNIQUEMENT par le texte exact de la bonne réponse.
                """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    return response.text.strip()