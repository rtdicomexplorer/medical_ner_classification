#normalizer.py
import requests
import time



UMLS_API_KEY = "YOUR_UMLS_API_KEY"   #rom https://uts.nlm.nih.gov/uts/ after registration
UMLS_BASE = "https://uts-ws.nlm.nih.gov/rest"
VERSION = "current"

def get_tgt_ticket():
    """Get the Ticket Granting Ticket (TGT) for UMLS authentication."""
    auth = requests.post(
        "https://utslogin.nlm.nih.gov/cas/v1/api-key",
        data={"apikey": UMLS_API_KEY}
    )
    if auth.status_code != 201:
        raise Exception("Could not get TGT: " + auth.text)
    return auth.headers["location"]

def get_service_ticket(tgt):
    """Get a single-use service ticket using the TGT."""
    resp = requests.post(tgt, data={"service": "http://umlsks.nlm.nih.gov"})
    if resp.status_code != 200:
        raise Exception("Could not get service ticket.")
    return resp.text

def search_cui(term, source="ICD10CM"):
    """
    Search a term in UMLS and return the code from the specified vocabulary.
    Example sources: 'ICD10CM', 'SNOMEDCT_US', 'RXNORM'
    """
    try:
        tgt = get_tgt_ticket()
        ticket = get_service_ticket(tgt)

        search_url = f"{UMLS_BASE}/search/{VERSION}"
        params = {
            "string": term,
            "ticket": ticket,
            "pageSize": 5,
            "returnIdType": "code",
            "sabs": source,
            "language": "ENG"
        }
        headers = {"Accept": "application/json"}

        resp = requests.get(search_url, headers=headers, params=params)
        resp.raise_for_status()
        results = resp.json().get("result", {}).get("results", [])

        if not results:
            return None

        first = results[0]
        cui = first["ui"]

        return get_code_from_cui(cui, source, ticket)

    except Exception as e:
        print(f"[UMLS Error] {e}")
        return None

def get_code_from_cui(cui, source, ticket):
    """Fetch atom-level details from a CUI and extract the relevant code."""
    url = f"{UMLS_BASE}/content/{VERSION}/CUI/{cui}/atoms"
    params = {
        "ticket": ticket,
        "language": "ENG",
        "sabs": source
    }
    headers = {"Accept": "application/json"}

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        return None

    atoms = resp.json().get("result", [])
    for atom in atoms:
        if atom["rootSource"] == source:
            return {
                "code": atom["code"],
                "source": source,
                "name": atom["name"]
            }

    return None
