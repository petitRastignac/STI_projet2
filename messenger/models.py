from messenger import DB

class Model(object):
    @classmethod
    def create_table(cls, columns_stmt):
        DB.engine.execute('CREATE TABLE {} ({})'.format(
            cls.__tablename__,
            columns_stmt
        ))

    @classmethod
    def insert(cls, columns, keys, values):
        stmt = DB.text('INSERT INTO {} ({}) VALUES ({})'.format(
            cls.__tablename__,
            columns,
            keys
        ))
        DB.engine.execute(stmt.bindparams(**values))

    @classmethod
    def select(cls, key, value):
        stmt = DB.text('SELECT * FROM {} WHERE {}=:{}'.format(
            cls.__tablename__,
            key,
            key
        ))
        return DB.engine.execute(stmt.bindparams(**{key: value}))

    @classmethod
    def delete(cls, key, value):
        stmt = DB.text('DELETE FROM {} WHERE {}=:{}'.format(
            cls.__tablename__,
            key,
            key
        ))
        return DB.engine.execute(stmt.bindparams(**{key: value}))

class User(Model):
    __tablename__ = 'users'

    def __init__(self, id, firstname, lastname, username, password):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password

    @classmethod
    def create_table(cls):
        super().create_table(
            'id INTEGER PRIMARY KEY AUTOINCREMENT, \
                firstname TEXT, \
                lastname TEXT, \
                username TEXT, \
                password TEXT'
        )

    @classmethod
    def insert(cls, firstname, lastname, username, password):
        super().insert(
            'firstname, lastname, username, password',
            ':firstname, :lastname, :username, :password',
            {
                'firstname': firstname, 'lastname': lastname,
                'username': username, 'password': password
            }
        )

    @classmethod
    def select(cls, user_id):
        res = super().select('id', user_id).fetchone()
        if res:
            return User(res[0], res[1], res[2], res[3], res[4])
        return None

    @classmethod
    def find(cls, username):
        return super().select('username', username).fetchone() != None

    @classmethod
    def delete(cls, user_id):
        super().delete('id', user_id)
