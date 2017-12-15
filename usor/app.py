from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import default_exceptions
from flask import request

from config import config
from .extentions import extensions, lm
from .resources import auth_api, user_api, role_api, admin_api
from .models.user import User
from .common.token import decode_token, get_token
from .common.flask import APIException, APIFlask
from .common.helpers import get_remote_addr


def create_app(env="default"):
    app = APIFlask(__name__)
    app.config.from_object(config[env])
    app.wsgi_app = ProxyFix(app.wsgi_app)

    #  initialize all extensions
    [ext.init_app(app) for ext in extensions]

    quick_errors_handling(app)
    config_lm()
    register_bp(app)

    @app.before_request
    def no_input_data():
        if request.method in ("POST", "PUT", "DELETE"):
            if not request.get_json():
                raise APIException("no data provided", 400)

    return app


def register_bp(app):
    app.register_blueprint(auth_api)
    app.register_blueprint(user_api, url_prefix="/user")
    app.register_blueprint(role_api, url_prefix="/role")
    app.register_blueprint(admin_api, url_prefix="/admin/user")


def quick_errors_handling(app):
    def errors_render(exception):
        resp = {"message": exception.name}
        return resp, exception.code
    for exception in default_exceptions:
        app.register_error_handler(exception, errors_render)

    @app.errorhandler(APIException)
    def handle_api_exception(exception):
        resp = exception.to_dict()
        return resp, exception.status_code


def config_lm():
    @lm.request_loader
    def load_header(request):
        token = get_token(request)
        payload = decode_token(token)
        if payload:
            user = User.get_user(payload["usor_id"])
            if user and payload["sid"] == user.sid:
                user.logged_ip = get_remote_addr()
                return user.save()
        return None

    @lm.unauthorized_handler
    def unauthorized():
        raise APIException("login required", 401)
