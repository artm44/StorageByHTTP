from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI
API_URL = '/static/swagger.json'

module = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "StorageByHTTP"
    }
)
