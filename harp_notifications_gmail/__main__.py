import harp_notifications_gmail.settings as settings
from fastapi import FastAPI, Request, status
from prometheus_fastapi_instrumentator import Instrumentator
from harp_notifications_gmail.api.health import router as health
from harp_notifications_gmail.api.notifications import router as notification_profile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from logger.logging import service_logger
from logger.logging import fastapi_logging
from harp_notifications_gmail.plugins.tracer import get_tracer
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


log = service_logger()
fastapi_logging()
tracer = get_tracer()


app = FastAPI(
    openapi_url=f'{settings.URL_PREFIX}/openapi.json',
    docs_url=f'{settings.URL_PREFIX}/docs',
    redoc_url=f'{settings.URL_PREFIX}/redoc'
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log.error(
        msg=f"FastAPI: Failed to validate request\nURL: {request.method} - {request.url}\nBody: {exc.body}\nError: {exc.errors()}"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
Instrumentator().instrument(app).expose(app)
app.include_router(health)
app.include_router(notification_profile)
