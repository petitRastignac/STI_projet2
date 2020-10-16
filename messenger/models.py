# ---------------------------
#Fichier : models.py
#Date : 14.10.2020
#But : implémentation de fonctions pour la gestion de la database
#Remarque :
#------------------------------

import datetime as dt

from messenger import DB
from messenger.security import gen_rand_string, hash_pw

def cols2keys(columns):
    return ''.join(
        ', :{}'.format(x.replace(' ', '')) for x in columns.split(',')
    )[2:]

def get_current_timestamp() -> int:
    return int((
        dt.datetime.now() + Session.SESSION_DURATION
    ).replace(microsecond=0).timestamp())

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
        """
        Execute a `INSERT INTO VALUES` command using the calling
        classe's `__tablename__` table.

        :param columns_stmt: SQL columns declaration
        :param key: column identifier to use
        :param value: value to insert
        """
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
    def update(cls, update_dict: dict, ident_key: str, ident_value: object) -> None:
        """
        Execute an `UPDATE` command on the calling classe's
        `__tablename__` table with the given parameters

        :param update_dict: mapping of columns to their new values
        :param ident_key: column to use in the `WHERE` clause
        :param ident_value: value to use in the `WHERE` clause
        """
        stmt = DB.text('UPDATE {} SET {} WHERE {IDENT_KEY}=:{IDENT_KEY}'.format(
            cls.__tablename__,
            ''.join(
                ', {}=:{}'.format(x, x) for x in update_dict
            )[2:],
            IDENT_KEY=ident_key
        ))

        # populate parameters dict
        params_dict = {ident_key: ident_value}
        for x in update_dict:
            params_dict[x] = update_dict[x]

        DB.engine.execute(stmt.bindparams(**params_dict))


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

    def __init__(self, admin: bool, active: bool, username: str, firstname: str, lastname: str, password: str):
        self.admin = admin
        self.active = active
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.messages = Message.from_recipient(self.username)

    def __str__(self):
        return '{} {} (@{})'.format(
            self.firstname, self.lastname, self.username
        )

    @classmethod
    def create_table(cls) -> None:
        """
        Create the user table
        """
        super().create_table(
            """
            admin BOOLEAN NOT NULL,
            active BOOLEAN NOT NULL,
            username VARCHAR({TEXT_LEN}) PRIMARY KEY,
            firstname VARCHAR({TEXT_LEN}) NOT NULL,
            lastname VARCHAR({TEXT_LEN}) NOT NULL,
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
        columns = 'admin, active, firstname, lastname, username, password'
        super().insert(
            columns=columns,
            keys=cols2keys(columns),
            values={
                'admin': admin, 'active': True,
                'firstname': firstname, 'lastname': lastname,
                'username': username, 'password': password
            }
        )

    @classmethod
    def select(cls, username: str):
        """
        Return the User with the given username, if it exists

        :param username: username to look for
        :return: User if username exists, else None
        """
        rows = super().select('username', username)
        if rows:
            return User(*rows[0])
        return None

    @classmethod
    def all(cls) -> list:
        rows = super().select('1', 1)
        if rows:
            return [User(*row) for row in rows]
        return None

    @classmethod
    def find(cls, username: str) -> bool:
        """
        Check whether a user with the given username exists

        :param username: username to look for
        :return: True if username is used by an account
        """
        return isinstance(cls.select(username), User)

    @classmethod
    def update(cls, username, update_dict):
        """
        Update user with the given username

        :param username: username to look for
        :param update_dict: column and content to update
        """
        super().update(update_dict, 'username', username)

    @classmethod
    def change_pass(cls, username, newpass):
        # update password
        cls.update(username, {'password': hash_pw(newpass)})

        # terminate all sessions
        Session.terminate_user(username)

    @classmethod
    def delete(cls, username: str) -> None:
        """
        Delete the user row with the given username

        :param username: username to look for and delete
        """
        user = cls.select(username)

        # delete user's inbox
        for msg in user.messages:
            Message.delete(msg.id)

        # delete user sessions
        Session.terminate_user(user.username)

        super().delete('username', username)

    @classmethod
    def from_session(cls, session_id: str):
        session = Session.select(session_id)
        return User.select(session.username)

class Session(Model):
    """
    Database model representing a user session
    """
    __tablename__ = 'sessions'

    SESSION_DURATION = dt.timedelta(hours=1)

    def __init__(self, session_id, username, expiry, ip, user_agent):
        self.id = session_id
        self.username = username
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
            username VARCHAR({TEXT_LEN}) NOT NULL,
            expiry INTEGER NOT NULL,
            ip VARCHAR({TEXT_LEN}) NOT NULL,
            user_agent VARCHAR({TEXT_LEN}) NOT NULL,
            CONSTRAINT `fk_session_username` FOREIGN KEY (username) REFERENCES users(username)
            """
        )

    @classmethod
    def insert(cls, session_id: str, username: str, expiry: int, ip: str, user_agent: str) -> None:
        """
        Create a session tied to the given user and with given parameters

        :param session_id: session ID
        :param username: username ID
        :param expiry: UNIX timestamp after which the session is invalid
        :param ip: IP for which the session is valid
        :param user_agent: user agent for which the session is valid
        """
        columns = 'id, username, expiry, ip, user_agent'
        super().insert(
            columns=columns,
            keys=cols2keys(columns),
            values={
                'id': session_id,
                'username': username,
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
    def from_user(cls, username):
        rows = super().select('username', username)
        if rows:
            return [Session(*row) for row in rows]
        return []

    @classmethod
    def terminate_user(cls, username):
        # https://youtu.be/ewZZNeYDiLo?t=32
        for sesh in cls.from_user(username):
            cls.delete(sesh.id)


    @classmethod
    def delete(cls, session_id: str) -> None:
        """
        Delete the session row with the given ID

        :param session_id: session ID to look for and delete
        """
        super().delete('id', session_id)

class Message(Model):
    __tablename__ = 'messages'

    def __init__(self, id, sender_name, recipient_name, date, title, body):
        self.id = id
        self.sender_name = sender_name
        self.recipient_name = recipient_name
        self.date = dt.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
        self.title = title
        self.body = body

    @classmethod
    def create_table(cls) -> None:
        """
        Create the user table
        """
        super().create_table(
            columns_stmt="""
            id VARCHAR({TEXT_LEN}) PRIMARY KEY,
            sender_name VARCHAR({TEXT_LEN}) NOT NULL,
            recipient_name VARCHAR({TEXT_LEN}) NOT NULL,
            date INTEGER NOT NULL,
            title VARCHAR({TEXT_LEN}) NOT NULL,
            body VARCHAR({TEXT_LEN}) NOT NULL,
            CONSTRAINT `fk_message_sender_name` FOREIGN KEY (sender_name) REFERENCES users(username),
            CONSTRAINT `fk_message_recipient_name` FOREIGN KEY (recipient_name) REFERENCES users(username)
            """
        )

    @classmethod
    def insert(cls, sender_name, recipient_name, date, title, body) -> None:
        """
        Insert a new message

        :param sender_name: username of the sender
        :param recipient_name: username of the receiver
        :param date: date when the message was sended
        :param title: title of the message
        :param body: the message itself
        """
        columns = 'id, sender_name, recipient_name, date, title, body'
        super().insert(
            columns=columns,
            keys=cols2keys(columns),
            values={
                'id': gen_rand_string('me'), 'sender_name': sender_name,
                'recipient_name': recipient_name,
                'date': date, 'title': title, 'body': body
            }
        )

    @classmethod
    def select(cls, message_id):
        """
        Select the message with the given ID

        :param message_id: message ID to look for
        """
        rows = super().select('id', message_id)
        if rows:
            return Message(*rows[0])
        return None

    @classmethod
    def from_sender(cls, sender_name):
        """
        Select all the messages sended by a user

        :param sender_name: username of the sender
        """
        rows = super().select('sender_name', sender_name)
        if rows:
            return [Message(*row) for row in rows]
        return None

    @classmethod
    def from_recipient(cls, recipient_name):
        """
        Select all the messages recived by a user

        :param recipient_name: username of the receiver
        """
        rows = super().select('recipient_name', recipient_name)
        if rows:
            return sorted(
                [Message(*row) for row in rows],
                key=lambda x: x.date,
                reverse=True
            )
        return []

    @classmethod
    def delete(cls, message_id: str) -> None:
        """
        Delete the message row with the given ID

        :param message_id: ID to look for and delete
        """
        super().delete('id', message_id)
