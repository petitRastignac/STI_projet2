import datetime as dt

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
    def create_table(cls, columns_stmt: str) -> None:
        """
        Execute a `CREATE TABLE` command using the calling classe's
        `__tablename__` table with the supplied columns statement

        :param columns_stmt: SQL columns declaration
        """
        DB.engine.execute('CREATE TABLE {} ({})'.format(
            cls.__tablename__,
            columns_stmt.format(TEXT_LEN=Model.TEXT_MAX_LEN),
        ))

    @classmethod
    def drop_table(cls) -> None:
        """
        Execute a `DROP TABLE IF EXISTS` command using the calling
        classe's `__tablename__` table.
        """
        DB.engine.execute('DROP TABLE IF EXISTS {}'.format(
            cls.__tablename__
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

    def __init__(self, id: str, admin: bool, firstname: str, lastname: str, username: str, password: str):
        self.id = id
        self.admin = admin
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
            """
            id VARCHAR({TEXT_LEN}) PRIMARY KEY,
            admin BOOLEAN NOT NULL,
            firstname VARCHAR({TEXT_LEN}) NOT NULL,
            lastname VARCHAR({TEXT_LEN}) NOT NULL,
            username VARCHAR({TEXT_LEN}) UNIQUE NOT NULL,
            password VARCHAR({TEXT_LEN}) NOT NULL
            """,
        )

    @classmethod
    def insert(cls, admin: bool, firstname: str, lastname: str, username: str, password: str) -> None:
        """
        Create a new user in the database with the supplied information

        :param admin: admin status
        :param firstname: first name
        :param lastname: last name
        :param username: username
        :param password: password
        """
        super().insert(
            'admin, id, firstname, lastname, username, password',
            ':admin, :id, :firstname, :lastname, :username, :password',
            {
                'admin': admin, 'id': gen_rand_string('us'),
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
            return User(*rows[0])
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

class Session(Model):
    """
    Database model representing a user session
    """
    __tablename__ = 'sessions'

    SESSION_DURATION = dt.timedelta(hours=1)

    def __init__(self, session_id, user_id, expiry, ip, user_agent):
        self.id = session_id
        self.user_id = user_id
        self.expiry = dt.datetime.fromtimestamp(expiry)
        self.ip = ip
        self.user_agent = user_agent

    @classmethod
    def create_table(cls) -> None:
        """
        Create the user table
        """
        super().create_table(
            columns_stmt="""
            id VARCHAR({TEXT_LEN}) PRIMARY KEY,
            user_id VARCHAR({TEXT_LEN}) NOT NULL,
            expiry INTEGER NOT NULL,
            ip VARCHAR({TEXT_LEN}) NOT NULL,
            user_agent VARCHAR({TEXT_LEN}) NOT NULL,
            CONSTRAINT `fk_session_user_id` FOREIGN KEY (user_id) REFERENCES users(id)
            """
        )

    @classmethod
    def insert(cls, session_id: str, user_id: str, expiry: int, ip: str, user_agent: str) -> None:
        """
        Create a session tied to the given user and with given parameters

        :param session_id: session ID
        :param user_id: user ID
        :param expiry: UNIX timestamp after which the session is invalid
        :param ip: IP for which the session is valid
        :param user_agent: user agent for which the session is valid
        """
        super().insert(
            columns='id, user_id, expiry, ip, user_agent',
            keys=':id, :user_id, :expiry, :ip, :user_agent',
            values={
                'id': session_id,
                'user_id': user_id,
                'expiry': expiry,
                'ip': ip,
                'user_agent': user_agent,
            }
        )

    @classmethod
    def select(cls, session_id: str):
        """
        Return the User with the given ID, if it exists

        :param user_id: user ID to look for
        :param find_by_id: whether to find user by ID or username
        :return: User if ID exists, else None
        """
        rows = super().select('id', session_id)
        if rows:
            return Session(*rows[0])
        return None

    @classmethod
    def delete(cls, session_id: str) -> None:
        """
        Delete the session row with the given ID

        :param session_id: session ID to look for and delete
        """
        super().delete('id', session_id)
