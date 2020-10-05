from messenger import DB

class Model(object):
    """
    Generic database model

    Implements helper methods to facilitate interaction with the
    database server
    """

    @classmethod
    def create_table(cls, columns_stmt: str) -> None:
        """
        Execute a `CREATE TABLE` command using the calling classe's
        `__tablename__` table with the supplied columns statement

        :param columns_stmt: SQL columns declaration
        """
        DB.engine.execute('CREATE TABLE {} ({})'.format(
            cls.__tablename__,
            columns_stmt
        ))

    @classmethod
    def insert(cls, columns: str, keys: str, values: dict) -> None:
        stmt = DB.text('INSERT INTO {} ({}) VALUES ({})'.format(
            cls.__tablename__,
            columns,
            keys
        ))
        DB.engine.execute(stmt.bindparams(**values))

    @classmethod
    def select(cls, key: str, value: object) -> list:
        """
        Execute a `SELECT` command on the calling classe's
        `__tablename__` table with the supplied key and value

        :param key: column identifier to use
        :param value: value to match in column to select
        :return: matching rows as a list
        """
        stmt = DB.text('SELECT * FROM {} WHERE {}=:{}'.format(
            cls.__tablename__,
            key,
            key
        ))
        return DB.engine.execute(stmt.bindparams(**{key: value})).fetchall()

    @classmethod
    def delete(cls: object, key: str, value: object) -> None:
        """
        Execute a `DELETE` command on the calling classe's
        `__tablename__` table with the supplied key and value

        :param key: column identifier to use for deletion
        :param value: value to match in column to delete row
        """
        stmt = DB.text('DELETE FROM {} WHERE {}=:{}'.format(
            cls.__tablename__,
            key,
            key
        ))
        DB.engine.execute(stmt.bindparams(**{key: value}))

class User(Model):
    """
    Database model representing a user
    """
    __tablename__ = 'users'

    def __init__(self, id: int, firstname: str, lastname: str, username: str, password: str):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password

    @classmethod
    def create_table(cls) -> None:
        """
        Create the user table
        """
        super().create_table(
            'id INTEGER PRIMARY KEY AUTOINCREMENT, \
                firstname TEXT, \
                lastname TEXT, \
                username TEXT, \
                password TEXT'
        )

    @classmethod
    def insert(cls, firstname: str, lastname: str, username: str, password: str) -> None:
        """
        Create a new user in the database with the supplied information

        :param firstname: first name
        :param lastname: last name
        :param username: username
        :param password: password
        """
        super().insert(
            'firstname, lastname, username, password',
            ':firstname, :lastname, :username, :password',
            {
                'firstname': firstname, 'lastname': lastname,
                'username': username, 'password': password
            }
        )

    @classmethod
    def select(cls, user_id: int, findById=True):
        """
        Return the User with the given ID, if it exists

        :param user_id: user ID to look for
        :param find_by_id: whether to find user by ID or username
        :return: User if ID exists, else None
        """
        rows = super().select('id' if findById else 'username', user_id)
        if rows:
            res = rows[0]
            return User(res[0], res[1], res[2], res[3], res[4])
        return None

    @classmethod
    def find(cls, username: str) -> bool:
        """
        Check whether a user with the given username exists

        :param username: username to look for
        :return: True if username is used by an account
        """
        return len(super().select('username', username)) > 0

    @classmethod
    def delete(cls, user_id: int) -> None:
        """
        Delete the user row with the given ID

        :param user_id: user ID to look for and delete
        """
        super().delete('id', user_id)
