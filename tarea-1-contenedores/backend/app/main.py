from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import tasks

app = FastAPI(title="To-Do API")

# Orígenes permitidos (incluye localhost y 127.0.0.1 por si acaso)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # puedes usar ["*"] en desarrollo si lo prefieres
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)

@app.get("/healthz")
def health():
    return {"ok": True}
