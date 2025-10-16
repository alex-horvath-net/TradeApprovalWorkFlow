import uvicorn
from trading_approval_process.api.main import app

if __name__ == "__main__":
    uvicorn.run(
        "trading_approval_process.api.main:app",
        host="127.0.0.1",
        port=8080,
        reload=True
    )
