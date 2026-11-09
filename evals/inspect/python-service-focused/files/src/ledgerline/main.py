from fastapi import FastAPI

from ledgerline.api.routes import router

app = FastAPI(title="ledgerline")
app.include_router(router, prefix="/v1")
