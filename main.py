import os
import random
import time
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from instagraapi import Client

# Credenciales seguras desde las variables de entorno de Easypanel
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
LINK_WHATSAPP = "https://wa.me"
SESSION_FILE = "session.json"

MESSAGE_TEMPLATE = (
    "Hola! 👋 ¿Vendes por Instagram o TikTok?.\n "
    "Mi Agente de IA en menos de 5 minutos analiza tu BIO (Biografía) de Instagram y/o TikTok y además te entrega:\n"
    "✅ Una BIO optimizada.\n"
    "✅ Un mini estudio de tu mercado: Nicho, subnicho, perfil cliente ideal, objeciones de compra.\n"
    "✅ Estrategia para vender más.\n"
    "✅ Matriz de contenido para Instagram 7 días con contenido, tema, Hook, CTA y prompt para utilizar en la IA de preferencia.\n"
    f"👉🖱️Solamente haz clic en el enlace tocando aquí: {LINK_WHATSAPP}"
)

def enviar_mensajes_en_horario():
    cl = Client()
    
    # Reutilizar sesión para evitar bloqueos por IP
    if os.path.exists(SESSION_FILE):
        try:
            print("Cargando sesión guardada desde session.json...")
            cl.load_settings(SESSION_FILE)
            cl.login(USERNAME, PASSWORD)
            print("Sesión reutilizada con éxito.")
        except Exception:
            print("La sesión guardada expiró. Iniciando sesión desde cero...")
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE)
    else:
        print("Iniciando sesión por primera vez...")
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)

    try:
        with open("prospectos.txt", "r") as f:
            prospectos = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("Error: No se encontró el archivo prospectos.txt en el servidor.")
        return

    print(f"Cargados {len(prospectos)} prospectos para enviar.")

    for usuario in list(prospectos):
        while True:
            ahora = datetime.now()
            hora_actual = ahora.hour
            
            if 7 <= hora_actual < 22:
                try:
                    print(f"[{ahora.strftime('%H:%M:%S')}] Enviando mensaje a {usuario}...")
                    user_id = cl.user_id_from_username(usuario)
                    cl.direct_send(MESSAGE_TEMPLATE, user_ids=[user_id])
                    print(f"Mensaje enviado a {usuario}.")
                    
                    prospectos.remove(usuario)
                    
                    # Guardar lista actualizada
                    with open("prospectos.txt", "w") as f:
                        f.write("\n".join(prospectos))
                    
                    espera = random.randint(600, 900)
                    print(f"Esperando {espera // 60} minutos para el siguiente envío...")
                    time.sleep(espera)
                    break 
                    
                except Exception as e:
                    print(f"Error con {usuario}: {e}. Pasando al siguiente en 5 minutos...")
                    time.sleep(300)
                    break
            else:
                print(f"[{ahora.strftime('%H:%M:%S')}] Fuera de horario. Esperando 15 minutos...")
                time.sleep(900)

# Esto ejecuta la función del bot automáticamente al iniciar FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.get_event_loop().run_in_executor(None, enviar_mensajes_en_horario)
    yield

# Creamos la aplicación FastAPI usando el ciclo de vida (lifespan)
app = FastAPI(lifespan=lifespan)

# Tu ruta original intacta
@app.get("/")
def home():
    return {
        "status": "OK",
        "service": "Instagram API funcionando"
    }
