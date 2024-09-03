from core.server import create_app
from core.config import config
app = create_app()


if __name__ == "__main__":
    # Run the app directly (for development purposes only)
    create_app().run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
