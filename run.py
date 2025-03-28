from web_app import create_app
from web_app.utils.logger import setup_logger

app = create_app()
logger = setup_logger()

if __name__ == '__main__':
    logger.info('Starting application...')
    app.run(host='0.0.0.0', port=5050, debug=True) 