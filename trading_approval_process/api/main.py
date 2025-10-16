from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from trading_approval_process.api.dependencies import get_trade_service
from trading_approval_process.api.routes.trades_router import router as trades_router
from trading_approval_process.api.routes.health_router import router as health_router

# --- Rate limiter setup ---
limiter = Limiter(key_func=get_remote_address)

app = FastAPI( title="Trade Approval API", version="1.0.0", docs_url="/api/docs", redoc_url="/api/redoc" )

# --- Middlewares ---
app.state.limiter = limiter
app.add_middleware( CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"] )

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    return JSONResponse(status_code=HTTP_429_TOO_MANY_REQUESTS, content={"error": "Too many requests"})

# --- Routers ---
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(trades_router, prefix="/api/trades", tags=["Trades"])
