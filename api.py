from settings import HOST, PORT
from ff_fasttext_api.server import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)