import google.generativeai as genai

genai.configure(api_key="AIzaSyBWo3n7UzzrACYTuRN5-lD3z8eyJ9tuxxg")  # Reemplaza con tu clave API

modelo = genai.GenerativeModel('models/gemini-1.5-pro-latest') # Usando el modelo correcto.

pregunta = "¿Cuál es la capital de Francia?"

respuesta = modelo.generate_content(pregunta)

print(respuesta.text)