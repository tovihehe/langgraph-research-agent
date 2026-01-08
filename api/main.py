from fastapi import FastAPI
from api.routes.agent import router as agent_router
from api.routes.auth import router as auht_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Agent API",
    description="API to interact with the Agent.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pruebas, en producción usa dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(agent_router, tags=["Agent"])
app.include_router(auht_router, tags=["Auth"])


