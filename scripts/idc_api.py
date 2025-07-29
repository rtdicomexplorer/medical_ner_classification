import requests

# Function to get OAuth token
def get_token(client_id, client_secret):

    try:

        resp = requests.post(
            "https://icdaccessmanagement.who.int/connect/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
                "scope": "icdapi_access"
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
    except Exception as e:
        print("Unable to get the token")
        return None
    
# Lookup description via ICD API
def fetch_icd_description(code, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2"
    }
    uri = f"https://id.who.int/icd/entity/{code}"
    resp = requests.get(uri, headers=headers)
    if resp.ok:
        data = resp.json()
        return data.get("title", {}).get("display", "Beschreibung unbekannt")
    return None