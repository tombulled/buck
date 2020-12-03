from buck.api import Api

api = Api \
(
    anonymous = True,
    path      = None,
)

# user = api.add_user \
# (
#     name       = 'User',
#     access_key = 'admin',
#     secret_key = 'admin',
# )

api.serve()
