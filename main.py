from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"status": "OK", "message": "OTT BI Tool is running"}
