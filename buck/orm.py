import inflection
import sqlalchemy.ext.declarative

def declarative_base():
    @sqlalchemy.ext.declarative.as_declarative()
    class BaseModel(object):
        @sqlalchemy.ext.declarative.declared_attr
        def __tablename__(cls):
            return inflection.underscore(cls.__name__)

    return BaseModel

class Database(object):
    def __init__(self, uri):
        engine_kwargs = {}

        if uri.startswith('sqlite'):
            engine_kwargs['connect_args'] = \
            {
                'check_same_thread': False,
            }

        self.engine = sqlalchemy.create_engine(
            uri,
            **engine_kwargs,
        )

        self._session_maker = sqlalchemy.orm.sessionmaker(
            bind = self.engine,
            autocommit = False,
            autoflush = False,
        )

        # self.models = utils.Models(self.base_model)

        # self.create_all()

    def __str__(self):
        return f'{self.__class__.__name__}()'

    def __repr__(self):
        return self.__str__()

    def __call__(self):
        session = self._session_maker()

        try:
            yield session
        finally:
            session.close()

    # def make_session(self):
    #     return self._session_maker()
    #
    # def yield_session(self):
    #     session = self.make_session()
    #
    #     try:
    #         yield session
    #     finally:
    #         session.close()
    #
    # def create_all(self):
    #     self.base_model.metadata.create_all(self.engine)
