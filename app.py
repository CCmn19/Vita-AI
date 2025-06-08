import os
import google.generativeai as genai
import markdown
import requests
# ¡Importante! Añadir jsonify para poder enviar respuestas en formato JSON
from flask import Flask, request, render_template, session, redirect, jsonify
from flask_session import Session
from dotenv import load_dotenv

def crear_app():
    # Cargar las variables de entorno
    load_dotenv()

    # Configuración de Flask
    app = Flask(__name__)
    app.secret_key = "clave_secreta_para_sesiones"
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # Configuración de AI
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")

    MAX_HISTORY = 10  # Aumentamos un poco el historial para un chat

    @app.route("/", methods=["GET", "POST"])
    def home():
        if "datos_usuario" not in session:
            session["datos_usuario"] = None
        if "history" not in session:
            session["history"] = []

        mensaje_bienvenida = None
        dieta_recomendada = None

        if request.method == "POST":
            # Este bloque POST ahora solo manejará los formularios iniciales
            if not session["datos_usuario"]:
                nombre = request.form.get("nombre")
                peso = request.form.get("peso")
                altura = request.form.get("altura")
                edad = request.form.get("edad")
                sexo = request.form.get("sexo")
                informacion_adicional = request.form.get("informacion_adicional")

                altura_metros = float(altura) / 100
                imc = float(peso) / (altura_metros ** 2)
                estado = ""
                dieta = ""
                
                if imc < 18.5:
                    estado = "Bajo peso"
                    dieta = "Dieta hipercalórica: rica en calorías saludables como frutos secos, aguacate, pastas y batidos."
                elif imc < 24.9:
                    estado = "Peso normal"
                    dieta = "Dieta equilibrada: frutas, verduras, proteínas magras, cereales integrales y grasas buenas."
                elif imc < 29.9:
                    estado = "Sobrepeso"
                    dieta = "Dieta hipocalórica: menos calorías, control de porciones y alimentos bajos en grasa."
                else:
                    estado = "Obesidad"
                    dieta = "Dieta baja en carbohidratos: proteínas, verduras y sin harinas ni azúcares refinados."

                session["datos_usuario"] = {
                    "nombre": nombre, "peso": peso, "altura": altura, "edad": edad,
                    "sexo": sexo, "informacion_adicional": informacion_adicional,
                    "dietas": None, "ejercicios": None,
                }

                mensaje_bienvenida = f"<strong>{nombre}</strong>, tu IMC es <strong>{imc:.2f}</strong> ({estado})."
                dieta_recomendada = f"<strong>✅ Dieta recomendada:</strong><br>{dieta}"
                
                # Renderizamos la plantilla para mostrar la pantalla de opciones
                return render_template("index.html",
                                    datos_usuario=session.get("datos_usuario"),
                                    history=session.get("history"),
                                    mensaje_bienvenida=mensaje_bienvenida,
                                    dieta_recomendada=dieta_recomendada)
            
            elif "dietas" in request.form and "ejercicios" in request.form:
                session["datos_usuario"]["dietas"] = request.form.get("dietas")
                session["datos_usuario"]["ejercicios"] = request.form.get("ejercicios")
                session.modified = True
                return redirect("/")
        
        # El método GET simplemente carga la página con los datos de la sesión
        return render_template("index.html",
                            datos_usuario=session.get("datos_usuario"),
                            history=session.get("history"),
                            mensaje_bienvenida=mensaje_bienvenida,
                            dieta_recomendada=dieta_recomendada)


    # --- NUEVA RUTA PARA EL CHAT ASÍNCRONO ---
    @app.route("/chat", methods=["POST"])
    def chat():
        # Obtener el mensaje del JSON enviado por JavaScript
        mensaje_usuario = request.json.get("mensaje")

        if not mensaje_usuario:
            return jsonify({"error": "No se recibió ningún mensaje."}), 400

        if "datos_usuario" not in session or not session["datos_usuario"]:
            return jsonify({"respuesta": "Por favor, completa primero tus datos de salud."})

        try:
            datos = session["datos_usuario"]
            contexto = f"El usuario se llama {datos['nombre']}, pesa {datos['peso']} kg y mide {datos['altura']} cm. Tiene {datos['edad']} años y es {datos['sexo']}. Su informacíon a tomar en cuenta es {datos['informacion_adicional']}. Su dieta es {datos['dietas']} y su plan de ejercicio es {datos['ejercicios']}. Solo si el usuario te pregunta tu nombre di que eres un asistente virtual de IA especializado en nutrición y entrenamiento físico llamado Vita AI. Despues de cada punto agrega un espacio para que el texto no se vea muy pegado"
            prompt = f"{contexto}\n\nHistorial de la conversación: {session.get('history', [])}\n\nPregunta actual del usuario: {mensaje_usuario}"

            respuesta_modelo = model.generate_content(prompt)
            respuesta_ia = respuesta_modelo.text

            # Guardar en el historial
            session["history"].append({"pregunta": mensaje_usuario, "respuesta": respuesta_ia})
            if len(session["history"]) > MAX_HISTORY:
                session["history"] = session["history"][-MAX_HISTORY:]
            session.modified = True
            
            # Devolver solo la respuesta de la IA en formato JSON
            return jsonify({"respuesta": respuesta_ia})

        except Exception as e:
            return jsonify({"error": f"Error al generar la respuesta: {str(e)}"}), 500
    return app


if __name__ == "__main__":
  app = crear_app()    
  app.run(debug=True)