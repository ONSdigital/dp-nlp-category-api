import logging.config

from category_api.server import create_app
from category_api.settings import settings
from gunicorn_config import logconfig_dict

# Configure logging using the provided logconfig_dict
logging.config.dictConfig(logconfig_dict)

app = create_app()
app.logger = logconfig_dict
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_config=logconfig_dict)
