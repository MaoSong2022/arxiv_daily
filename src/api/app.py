from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config.settings import settings
from ..utils.logging import setup_logging
from . import routes


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application.
    """
    # Set up logging
    setup_logging()

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="API for your application",
        version="0.1.0",
        debug=settings.debug,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update with your allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(routes.router)

    return app


app = create_app()
