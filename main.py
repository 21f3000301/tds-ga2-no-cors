from collections import defaultdict
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# added for another assignment in tds-ga2-may2026, OAuth 2.0 / OIDC Token Verification Service (2 marks)
from pydantic import BaseModel
import jwt
from jwt import InvalidTokenError
from jwt.exceptions import ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError



API_KEY = "ak_mo5txj6vie7amnmopjwlwmaa"
EMAIL = "21f3000301@ds.study.iitm.ac.in"  # replace with your logged-in email

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analytics")
async def analytics(request: Request):
    api_key = request.headers.get("x-api-key")  # read directly

    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    events = body.get("events", [])

    total_events = len(events)
    unique_users = len({e.get("user") for e in events})

    revenue = 0.0
    user_positive_totals = defaultdict(float)

    for event in events:
        user = event.get("user")
        amount = float(event.get("amount", 0))

        if amount > 0:
            revenue += amount
            user_positive_totals[user] += amount

    top_user = max(user_positive_totals, key=user_positive_totals.get) if user_positive_totals else ""

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user,
    }

# for another assignment in tds-ga2-may2026, OAuth 2.0 / OIDC Token Verification Service (2 marks)
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

EXPECTED_ISSUER = "https://idp.exam.local"
EXPECTED_AUDIENCE = "tds-bm5851cc.apps.exam.local"

class VerifyRequest(BaseModel):
    token: str

@app.post("/verify")
def verify(req: VerifyRequest):
    try:
        payload = jwt.decode(
            req.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience=EXPECTED_AUDIENCE,
            issuer=EXPECTED_ISSUER,
            options={
                "require": ["exp", "iss", "aud", "sub"],
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            },
        )

        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud"),
        }

    except (ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError, InvalidTokenError):
        raise HTTPException(status_code=401, detail={"valid": False})
