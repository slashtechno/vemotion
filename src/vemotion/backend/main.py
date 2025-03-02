import importlib
import json
from pathlib import Path
import uuid
from fastapi.responses import RedirectResponse
import httpx
from pydantic import BaseModel, Field
from slack_sdk import WebClient
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vemotion import settings
from vemotion.consts import SLACK_OAUTH_ACCESS_URL, SLACK_OAUTH_REDIRECT_URI
from vemotion.cv import cv

# SLACK_CLIENT_ID = settings.slack_client_id
# SLACK_OAUTH_REDIRECT_URI = "https://localhost:8443/oauth/callback"
# SLACK_OAUTH_AUTHORIZE_URL = "https://slack.com/oauth/v2/authorize"
# SLACK_OAUTH_ACCESS_URL = "https://slack.com/api/oauth.v2.access"

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

# class AuthResponse(BaseModel):
    # Can't be a default value (id: uuid.UUID = uuid.uuid4()) since that would only be evaluated once and all instances would share the same id
    # id: uuid.UUID = Field(default_factory=uuid.uuid4)


@app.get("/oauth/callback")
async def oauth_callback(code: str = None, error: str = None) -> RedirectResponse:
    if error:
        raise HTTPException(status_code=400, detail=f"Error from Slack: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code parameter")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            SLACK_OAUTH_ACCESS_URL,
            data={
                "client_id": settings.slack_client_id,
                "client_secret": settings.slack_client_secret,
                "code": code,
                "redirect_uri": SLACK_OAUTH_REDIRECT_URI,
            },
        )
    data = response.json()
    if not data.get("ok"):
        raise HTTPException(status_code=400, detail=f"Slack OAuth failed: {data.get('error')}")
    # create a uuid4 as a session id
    session_id = uuid.uuid4()
    # save the session_id-access_token pair to settings.db_path (a JSON file)
    db_path = Path(settings.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        with open(db_path, "r") as f:
            db = json.load(f)
    else:
        db = {}
    db[str(session_id)] = data["authed_user"]["access_token"]
    with open(db_path, "w") as f:
        json.dump(db, f)
    # Direct the user to settings.frontend_url with the session_id as a query parameter
    return RedirectResponse(
        f"{settings.frontend_url}?session_id={session_id}",
    )

class Upload(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded image")
    access_token: str = Field(..., description="UUID4 session id")
@app.post("/")
async def upload_image(upload: Upload):
    result = cv.analyze_frame(
        cv.base64_to_opencv_image(upload.image_base64)
    )
    # Based on the result, set the status in Slack
    # Get the access token from the database
    db_path = Path(settings.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.exists():
        raise HTTPException(status_code=400, detail="No access token found")
    with open(db_path, "r") as f:
        db = json.load(f)
    # Get the access token from the database
    access_token = db.get(upload.access_token)
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token found")
    # Set the status in Slack
    client = WebClient(token=access_token)
    response = client.users_profile_set(
    profile={
            "status_text": result.dominant_emotion,
            "status_emoji": result.emoji,
        }
    )
    return response["ok"]

if __name__ == "__main__":
    # Go to http://localhost:8000/docs to see the Swagger UI
    # or http://localhost:8000/redoc to see the specification
    uvicorn.run(app, host="0.0.0.0", port=8000)
