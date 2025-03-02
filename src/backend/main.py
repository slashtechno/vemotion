import importlib
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamically import all routers
routers_dir = Path(__file__).parent / "routers"
for path in routers_dir.glob("*.py"):
    if path.name != "__init__.py":
        module_name = f"podium.routers.{path.stem}"
        module = importlib.import_module(module_name)
        # If the module has a router attribute, include it in the app
        if hasattr(module, "router"):
            app.include_router(getattr(module, "router"))

@app.get("/")

if __name__ == "__main__":
    # Go to http://localhost:8000/docs to see the Swagger UI
    # or http://localhost:8000/redoc to see the specification
    uvicorn.run(app, host="0.0.0.0", port=8000)
