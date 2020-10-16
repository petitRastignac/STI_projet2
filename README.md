# STI project 1

## Table of contents

- [Introduction](#introduction)
- [Usage](#usage)
- [Authors](#authors)

## Introduction

_Messenger_ is a simple communication webapp where users can send short text messages to one another.

## Usage

You can either use this app [locally](#local) or [through Docker](#docker).

To test admin functionality an admin account is automatically, username: admin password: admin.

### Local

__Step 1: Database__

You will need a MySQL or MariaDB server running, and also to create the database.

You can use Docker to launch a MariaDB server:

```
docker run -e MYSQL_ROOT_PASSWORD=sti -p 3306:3306 -d --name sti_db_dev mariadb
```

Create the database:

```
docker exec -it sti_db_dev mysql -u root -p -e "DROP DATABASE IF EXISTS sti; CREATE DATABASE sti;"
```

Then set the appropriate credentials like so:

```
export STI_MSN_DB=mysql+pymysql://USER:PASS@HOST/DATABASE
```

where:

- `USER` is the database user,
- `PASS` is `USER`'s password,
- `HOST` is the database hostname or IP address,
- `DATABASE` is the database for which USER has full rights.

For instance, use:

```
export STI_MSN_DB=mysql+pymysql://root:sti@HOST/sti
```

Remember to change `HOST` by an actual value. You can use `docker inspect` to retrieve a container's IP address.

__Step 2: Python__

You will need a virtual environment created like so:

```
python3 -m venv venv
. venv/bin/activate # Windows users will use \venv\Scripts\activate.bat
```

Install dependencies:

```
pip install -Ue .
```

Set up the database schema:

```
export FLASK_APP=messenger
python scripts/devseed.py
```

Lastly, run the webapp with the development server:

```
flask run
```

Messenger is now available at [http://localhost:5000](http://localhost:5000).

To enable debug mode, also set:

```
export FLASK_DEBUG=True
```

### Docker

Assuming you already have Docker working, simply use `docker-compose`:

```
docker-compose up -d
docker exec -it sti_uwsgi python /app/scripts/devseed.py

```

The last command initializes the database schema (can also be used to wipe the database clean).

Messenger is now available at [http://localhost:12321](http://localhost:12321).

Note: when running Docker in the foreground, killing the stack requires a double `Ctrl+C`.

You may use Adminer to access the database using a convenient GUI available at [http://localhost:45654](http://localhost:45654). Use the following credentials:

- Server: `sti_db`
- Username: `sti`
- Password: `stipass`
- Database: `sti`

## Authors

Messenger is made by:

- Diluckshan RAVINDRANATHAN
- Eric NOËL
- Moïn DANAI
