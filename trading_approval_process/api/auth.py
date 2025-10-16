from fastapi import Header, HTTPException

async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    # Normally decode JWT here
    return {"user": "user1@example.com"}
