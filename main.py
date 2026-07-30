from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def home():
    return {
        "status": "OK",
        "service": "Instagram API funcionando"
    }
