import json
import datetime
import os
import subprocess
import time
import google.generativeai as genai
import re
import requests

# Reemplaza con tu clave de API de Gemini
GEMINI_API_KEY = "AIzaSyBWo3n7UzzrACYTuRN5-lD3z8eyJ9tuxxg"

def configure_gemini_api(api_key):
    """Configura la API de Gemini con la clave proporcionada."""
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('models/gemini-1.5-pro-latest')
    except Exception as e:
        print(f"Error al configurar la API de Gemini: {e}")
        return None

def extract_json_from_response(content):
    """Extrae el contenido JSON de la respuesta de la IA usando varios métodos."""
    print("Iniciando extracción avanzada de JSON...")
    
    # Método 1: Extracción de bloques de código markdown
    if "```" in content:
        content = content.split("```")[1].strip()
    
    # Método 2: Uso de expresiones regulares para encontrar JSON
    json_pattern = re.compile(r'\{(?:[^{}]|(?R))*\}')
    json_matches = json_pattern.findall(content)
    
    if json_matches:
        return json.loads(json_matches[0])
    
    # Método 3: Búsqueda de secciones específicas
    if "Preguntas:" in content and "Respuestas:" in content:
        preguntas_text = content.split("Preguntas:")[1].split("Respuestas:")[0].strip()
        respuestas_text = content.split("Respuestas:")[1].strip()
        return {
            "preguntas": json.loads(preguntas_text),
            "respuestas": json.loads(respuestas_text)
        }
    
    # Si no se puede extraer JSON, devolver None
    return None

def generate_structured_questions(model, existing_data):
    """Genera preguntas en formato estructurado usando la API de Gemini."""

    if model is None:
        return {"preguntas": [], "respuestas": []}

    prompt = f"""
    Basado en los siguientes datos del usuario, genera 5 preguntas personalizadas.

    DATOS DEL USUARIO:
    {json.dumps(existing_data, indent=2, ensure_ascii=False)}

  INSTRUCCIONES:
1. Genera exactamente 5 preguntas personalizadas basadas en los datos del usuario.
2. Cada pregunta debe abordar una categoría específica:
   - temperatura
   - actividad_fisica
   - alimentacion
   - ruido
   - iluminacion
3. Las preguntas deben estar diseñadas para evaluar y mejorar el bienestar del usuario según sus datos previos.
4. Cada pregunta debe permitir una respuesta cuantificable del 1 al 5, donde:
   - 1 = Muy insatisfecho
   - 2 = Insatisfecho
   - 3 = Neutral
   - 4 = Satisfecho
   - 5 = Muy satisfecho

FORMATO OBLIGATORIO:
La respuesta debe estructurarse en JSON, dividiendo el contenido en dos secciones: "Preguntas" y "Respuestas".

- Sección "Preguntas": Contendrá un array de objetos, cada uno con la siguiente estructura exacta:
  {
      "categoria": "nombre_categoria",
      "pregunta": "¿Texto de la pregunta correspondiente?",
      "descripcion": "Breve descripción de por qué esta pregunta es relevante"
  }
  Cada objeto debe estar orientado a una de las siguientes categorías: temperatura, actividad_fisica, alimentacion, ruido, iluminacion.

- Sección "Respuestas": Contendrá un array de objetos con respuestas iniciales, siguiendo la misma secuencia de categorías que en "Preguntas". Cada objeto tendrá la siguiente estructura:
  {
      "categoria": "nombre_categoria",
      "valor": número_inicial_en_la_escala (valor entre 1 y 5)
  }

EJEMPLO DE SALIDA:
{
    "Preguntas": [
        {
            "categoria": "temperatura",
            "pregunta": "¿Qué tan cómodo te sientes con la temperatura en tu entorno actual?",
            "descripcion": "La temperatura afecta tu confort y bienestar. Ajustarla adecuadamente puede mejorar tu descanso y productividad."
        },
        {
            "categoria": "actividad_fisica",
            "pregunta": "¿Cuánto disfrutas tu nivel actual de actividad física diaria?",
            "descripcion": "La actividad física es clave para la salud física y mental. Evaluarla ayuda a mejorar tu rutina."
        },
        {
            "categoria": "alimentacion",
            "pregunta": "¿Qué tan satisfecho estás con la calidad de tu alimentación hoy?",
            "descripcion": "Una alimentación balanceada es fundamental para la energía y bienestar general."
        },
        {
            "categoria": "ruido",
            "pregunta": "¿Cómo calificarías el nivel de ruido en tu entorno?",
            "descripcion": "El ruido excesivo puede afectar tu concentración, descanso y estado de ánimo."
        },
        {
            "categoria": "iluminacion",
            "pregunta": "¿Qué tan adecuada consideras la iluminación en tu espacio?",
            "descripcion": "Una buena iluminación mejora la productividad y reduce el cansancio ocular."
        }
    ],
    "Respuestas": [
        { "categoria": "temperatura", "valor": 3 },
        { "categoria": "actividad_fisica", "valor": 4 },
        { "categoria": "alimentacion", "valor": 2 },
        { "categoria": "ruido", "valor": 3 },
        { "categoria": "iluminacion", "valor": 5 }
    ]
}

IMPORTANTE:
- Devuelve SOLO el JSON estructurado como se indicó, sin explicaciones ni texto adicional.
- Las preguntas deben ser específicas, personalizadas y medibles.
- Las respuestas deben ser valores numéricos del 1 al 5.

    """

    try:
        print("Enviando prompt de formato estructurado a Gemini...")
        response = model.generate_content(prompt)
        response.resolve()

        print("Extrayendo JSON de la respuesta...")
        content = response.text.strip()

        # Extrae el contenido JSON usando el nuevo método
        structured_output = extract_json_from_response(content)

        if structured_output is None:
            # Imprime el texto original de la respuesta si no se puede parsear como JSON
            print("\nRespuesta de Gemini (no se pudo parsear como JSON):")
            print(content)
            structured_output = {"preguntas": [], "respuestas": []}

        print("¡Preguntas estructuradas generadas exitosamente!")
        return structured_output
    except Exception as e:
        print(f"Error al generar preguntas con Gemini: {e}")
        return {"preguntas": [], "respuestas": []}

def fetch_data_from_endpoint(endpoint_url=None):
    """Obtiene datos del usuario desde un endpoint o una conexión SignalR."""
    print("\nObteniendo datos del usuario desde el endpoint...")
    
    # URL por defecto si no se proporciona una
    if not endpoint_url:
        endpoint_url = "https://backendhackathon202520250328210710.azurewebsites.net/hubs/gemini"
    
    try:
        # Intenta obtener los datos del endpoint
        response = requests.get(endpoint_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("Datos obtenidos exitosamente del endpoint.")
            return data
        else:
            print(f"Error al obtener datos del endpoint. Código: {response.status_code}")
            return None
    except Exception as e:
        print(f"No se pudo conectar al endpoint: {e}")
        return None

def get_user_data_source():
    """Permite al usuario elegir la fuente de datos."""
    print("\n" + "=" * 50)
    print("SELECCIÓN DE FUENTE DE DATOS")
    print("=" * 50)
    print("1. Usar datos de ejemplo")
    print("2. Obtener datos desde endpoint")
    
    choice = ""
    while choice not in ["1", "2"]:
        choice = input("\nSeleccione una opción (1-2): ")
        
    if choice == "1":
        print("Usando datos de ejemplo.")
        return get_example_data()
    else:
        endpoint_data = fetch_data_from_endpoint()
        if endpoint_data:
            # Adaptar el formato de los datos si es necesario
            user_data = format_endpoint_data(endpoint_data)
            return user_data
        else:
            print("No se pudieron obtener datos del endpoint. Usando datos de ejemplo como respaldo.")
            return get_example_data()

def format_endpoint_data(endpoint_data):
    """Formatea los datos del endpoint al formato esperado para generar preguntas."""
    try:
        # Si los datos ya vienen en el formato esperado, simplemente devuélvelos
        if isinstance(endpoint_data, dict) and "nombre" in endpoint_data:
            return endpoint_data
            
        # Si los datos vienen como un array (por ejemplo, un registro de una tabla)
        if isinstance(endpoint_data, list) and endpoint_data:
            # Tomar el primer registro
            record = endpoint_data[0]
            
            # Asegurarse de que tenga los campos necesarios
            required_fields = ["nombre", "edad", "actividad_fisica", "alimentacion", 
                            "temperatura_interior", "movimiento_diario", "frecuencia_ruido", "nivel_luz"]
            
            formatted_data = {}
            
            # Intentar extraer y mapear los campos
            for field in required_fields:
                if field in record:
                    formatted_data[field] = record[field]
            
            # Si no hay suficientes campos, complementar con valores por defecto
            if len(formatted_data) < len(required_fields):
                default_data = get_example_data()
                for field in required_fields:
                    if field not in formatted_data:
                        formatted_data[field] = default_data.get(field, "")
            
            return formatted_data
        
        # Si ninguno de los formatos anteriores funciona, convertir al formato esperado
        print("Formato de datos del endpoint no reconocido. Adaptando al formato esperado...")
        
        # Crear estructura básica
        formatted_data = {
            "nombre": "Usuario",
            "edad": 30,
            "actividad_fisica": "Moderada",
            "alimentacion": 5,
            "interaccion_social": 5,
            "ocio": 5,
            "productividad": 5,
            "temperatura_interior": "20°C",
            "movimiento_diario": "20 minutos",
            "frecuencia_ruido": "40dB",
            "nivel_luz": "350 lux"
        }
        
        # Intentar extraer valores del endpoint_data y actualizar formatted_data
        if isinstance(endpoint_data, dict):
            for key, value in endpoint_data.items():
                formatted_data[key] = value
        
        return formatted_data
        
    except Exception as e:
        print(f"Error al formatear datos del endpoint: {e}")
        return get_example_data()

def get_example_data():
    """Devuelve datos de ejemplo para el usuario."""
    return {
        "nombre": "Marco",
        "edad": 30,
        "actividad_fisica": "Moderada",
        "alimentacion": 7,
        "interaccion_social": 8,
        "ocio": 6,
        "productividad": 9,
        "temperatura_interior": "18°C",
        "movimiento_diario": "25 minutos",
        "frecuencia_ruido": "35dB",
        "nivel_luz": "400 lux"
    }

def generate_questions_json():
    """Genera JSON con 5 preguntas usando la API de Gemini."""

    print("Generando preguntas personalizadas usando la API de Gemini...")

    # Obtener datos del usuario, ya sea de ejemplo o del endpoint
    existing_data = get_user_data_source()
    
    print(f"\nGenerando preguntas para usuario: {existing_data.get('nombre', 'Desconocido')}")
    print("Datos del usuario:")
    for key, value in existing_data.items():
        print(f"  - {key}: {value}")

    try:
        print("Configurando la API de Gemini...")
        model = configure_gemini_api(GEMINI_API_KEY)
        if model is None:
            raise Exception("No se pudo configurar la API de Gemini")
        print("Generando preguntas personalizadas basadas en los datos del usuario...")
        questions_data = generate_structured_questions(model, existing_data)

        if not questions_data["preguntas"]:
            raise Exception("No se pudieron generar preguntas personalizadas")

    except Exception as e:
        print(f"Error: {e}")
        print("Generando preguntas personalizadas basadas en los datos disponibles...")

        # Fallback: generar preguntas personalizadas basadas en los datos del usuario
        questions_data = {
            "preguntas": [
                {
                    "categoria": "temperatura",
                    "pregunta": f"¿Prefieres mantener tu temperatura interior actual de {existing_data.get('temperatura_interior', '18°C')} o preferirías ajustarla?",
                    "descripcion": f"Basado en tu temperatura interior actual de {existing_data.get('temperatura_interior', '18°C')}"
                },
                {
                    "categoria": "actividad_fisica",
                    "pregunta": f"Actualmente realizas {existing_data.get('movimiento_diario', '25 minutos')} de actividad física. ¿Qué actividades te gustaría incorporar para llegar a 30 minutos?",
                    "descripcion": f"Considerando tu nivel de actividad física {existing_data.get('actividad_fisica', 'Moderada')}"
                },
                {
                    "categoria": "alimentacion",
                    "pregunta": f"Tu alimentación actual tiene una calificación de {existing_data.get('alimentacion', 7)}/10. ¿Qué aspecto específico te gustaría mejorar?",
                    "descripcion": f"Con base en tu calificación actual de alimentación ({existing_data.get('alimentacion', 7)}/10)"
                },
                {
                    "categoria": "ruido",
                    "pregunta": f"Con un nivel de ruido de {existing_data.get('frecuencia_ruido', '35dB')}, ¿cómo afecta esto a tu concentración durante el día?",
                    "descripcion": f"Tomando en cuenta tu nivel de ruido actual ({existing_data.get('frecuencia_ruido', '35dB')})"
                },
                {
                    "categoria": "iluminacion",
                    "pregunta": f"¿El nivel de luz actual de {existing_data.get('nivel_luz', '400 lux')} es cómodo para tus actividades principales?",
                    "descripcion": f"Considerando tu nivel de luz actual ({existing_data.get('nivel_luz', '400 lux')})"
                }
            ],
            "respuestas": []
        }

    # Formatear la data en la estructura JSON final
    questions_json_data = {
        "Text": "personalized_questions",
        "Timestamp": datetime.datetime.now().isoformat(),
        "AdditionalData": {
            "usuario": existing_data["nombre"],
            "datos": questions_data
        }
    }

    # Guardar la data en message_data.json
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "message_data.json")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questions_json_data, f, indent=2, ensure_ascii=False)

    print(f"Datos JSON de preguntas personalizadas generados y guardados en: {output_path}")
    print(f"Vista previa del contenido JSON:")
    print(json.dumps(questions_json_data, indent=2, ensure_ascii=False)[:500] + "...")

    return output_path

def run_csharp_app():
    """Ejecuta la aplicación C# SignalR para enviar los datos JSON."""

    print("\nEjecutando la aplicación C# para enviar los datos...")

    # Ruta al directorio del proyecto C# y al archivo Program.cs
    project_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        # Ejecutar la aplicación usando dotnet run en lugar del exe
        process = subprocess.Popen(
            ["dotnet", "run", "--project", project_dir],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True
        )

        # Imprimir la salida en tiempo real
        print("\nSalida de la aplicación C#:")
        print("-" * 50)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

                # Si se muestra el mensaje "Press any key to exit...", se envía una pulsación de Enter
                if "Press any key to exit" in output:
                    time.sleep(1)
                    process.terminate()
                    break

        # Obtener cualquier salida o error restante
        stdout, stderr = process.communicate()

        if stdout:
            print(stdout)

        if stderr:
            print("Errores:")
            print(stderr)

        print("-" * 50)

        if process.returncode == 0:
            print("¡Aplicación C# ejecutada exitosamente!")
            return True
        else:
            print(f"La aplicación C# salió con el código: {process.returncode}")
            return False

    except Exception as e:
        print(f"Error al ejecutar la aplicación C#: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("  GENERADOR DE PREGUNTAS PERSONALIZADAS Y ENVIADOR SIGNALR")
    print("=" * 70)

    json_path = generate_questions_json()

    print("\nEsperando 2 segundos antes de ejecutar la aplicación C#...")
    time.sleep(2)

    success = run_csharp_app()

    if success:
        print("\n¡Proceso completo exitosamente!")
    else:
        print("\nProceso completado con errores.")

    print("\nPresiona Enter para salir...")
    input()