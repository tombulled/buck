from .api import Api

def api(path: str = None, auth: tuple = ()):
    app: Api = Api \
    (
        anonymous = not auth,
        path      = path,
    )

    for access_key, secret_key in auth:
        app.add_user \
        (
            name       = 'User',
            access_key = access_key,
            secret_key = secret_key,
        )

    return app
