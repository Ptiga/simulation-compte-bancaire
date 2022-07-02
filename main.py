from fastapi import FastAPI

#Pour démarrer le serveur:
#python -m uvicorn main:app --reload

app = FastAPI()



@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test-api")
async def root():
    return {"message": "c'est une seconde route"}