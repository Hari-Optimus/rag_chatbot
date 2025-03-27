from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# Constants
TOKEN_URL = "https://defaultb5db11ac8f374109a1465d7a302f58.81.environment.api.powerplatform.com/powervirtualagents/botsbyschema/cra7c_agent4kbpPx/directline/token?api-version=2022-03-01-preview"
COPILOT_ENDPOINT = "https://defaultb5db11ac8f374109a1465d7a302f58.81.environment.api.powerplatform.com/powervirtualagents/botsbyschema/cra7c_agent4kbpPx/directline/token?api-version=2022-03-01-preview"
CLIENT_ID = "1cea657c-c9d0-4b4c-a4a1-a89d3afe2db4"
CLIENT_SECRET = "BWB8Q~jYD2m16Cmmb94n3MU.nCJHUFHQKaWUrb60"
REDIRECT_URI = "https://token.botframework.com/.auth/web/redirect"

def get_access_token():
    response = requests.get(TOKEN_URL)
    if response.status_code == 200:
        data = response.json()
        return data["token"], data["conversationId"]
    else:
        raise Exception("Failed to retrieve Direct Line token: " + response.text)

@app.post("/query")
async def query_copilot(auth_code: str, user_query: str):
    # Step 1: Exchange auth code for access token
    access_token = get_access_token(auth_code)
    
    # Step 2: Query Copilot Studio with the access token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"query": user_query}
    response = requests.post(COPILOT_ENDPOINT, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())
