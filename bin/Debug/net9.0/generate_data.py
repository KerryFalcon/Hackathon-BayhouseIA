import json
import datetime
import random

def generate_message_data():
    categories = ["vivienda", "salud", "educación", "transporte", "alimentación"]
    
    # Generate random data
    data = {
        "Text": random.choice(["casa", "hospital", "escuela", "onu", "ayuda"]),
        "Timestamp": datetime.datetime.now().isoformat(),
        "AdditionalData": {
            "categoria": random.choice(categories),
            "prioridad": random.randint(1, 5),
            "coordenadas": {
                "lat": 19.4326 + random.uniform(-0.1, 0.1),
                "lng": -99.1332 + random.uniform(-0.1, 0.1)
            },
            "temperatura": round(random.uniform(18, 32), 1),
            "humedad": random.randint(30, 90)
        }
    }
    
    # Save to a JSON file
    with open("message_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON data generated and saved to 'message_data.json'")

if __name__ == "__main__":
    generate_message_data()
