from collections import defaultdict
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

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
async def analytics(request: Request, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    if x_api_key != API_KEY:
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
