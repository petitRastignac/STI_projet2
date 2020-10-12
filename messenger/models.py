from messenger import DB
from messenger.security import gen_rand_string

class Model(object):
    """
    Generic database model

    Implements helper methods to facilitate interaction with the
    database server
    """

    TEXT_MAX_LEN = 200

    @classmethod
    def create_table(cls, columns_stmt: str, drop=False) -> None:
        """
        Execute a `CREATE TABLE` command using the calling classe's
        `__tablename__` table with the supplied columns statement

        If `drop` is true, a `DROP TABLE IF EXISTS` command will
        be issued beforehand.

        :param columns_stmt: SQL columns declaration
        """
        if drop:
            DB.engine.execute('DROP TABLE IF EXISTS {}'.format(
                cls.__tablename__
            ))

        DB.engine.execute('CREATE TABLE {} ({})'.format(
            cls.__tablename__,
            columns_stmt.format(TEXT_LEN=Model.TEXT_MAX_LEN),
        ))

        print(columns_stmt.format(TEXT_LEN=Model.TEXT_MAX_LEN))

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

    def __init__(self, id: str, firstname: str, lastname: str, username: str, password: str):
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
            'id VARCHAR({TEXT_LEN}) PRIMARY KEY, \
                firstname VARCHAR({TEXT_LEN}), \
                lastname VARCHAR({TEXT_LEN}), \
                username VARCHAR({TEXT_LEN}), \
                password VARCHAR({TEXT_LEN})',
            True
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
            'id, firstname, lastname, username, password',
            ':id, :firstname, :lastname, :username, :password',
            {
                'id': gen_rand_string('us'),
                'firstname': firstname, 'lastname': lastname,
                'username': username, 'password': password
            }
        )

    @classmethod
    def select(cls, user_id: str, findById=True):
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
    def delete(cls, user_id: str) -> None:
        """
        Delete the user row with the given ID

        :param user_id: user ID to look for and delete
        """
        super().delete('id', user_id)
