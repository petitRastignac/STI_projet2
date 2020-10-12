# STI project 1

## Table of contents

- [Introduction](#introduction)
- [Usage](#usage)
- [Authors](#authors)

## Introduction

_Messenger_ is a simple communication webapp where users can send short text messages to one another.

## Usage

You can either use this app [locally](#local) or [through Docker](#docker).

### Local

__Step 1: Database__

You will need a MySQL or MariaDB server running. Once that is done, set the appropriate credentials like so:

```
export STI_MSN_DB=mysql+pymysql://USER:PASS@HOST/DATABASE
```

where:

- `USER` is the database user,
- `PASS` is `USER`'s password,
- `HOST` is the database hostname or IP address,
- `DATABASE` is the database for which USER has full rights.

A sample script to do so is:

```
CREATE USER 'sti'@'%' IDENTIFIED BY 'sti';
CREATE DATABASE sti;
GRANT ALL PRIVILEGES ON sti.* TO 'sti'@'%' IDENTIFIED BY 'sti';
```

and then

```
export STI_MSN_DB=mysql+pymysql://sti:sti@HOST/sti
```

Remember to change `HOST` by an actual value.

__Step 2: Python__

You will need a virtual environment created like so:

```
python3 -m venv venv
```

Install dependencies:

```
pip install -Ue .
```

Lastly, run the webapp with the development server:

```
export FLASK_APP=messenger
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
docker compose build --no-cache
docker-compose up
```

Messenger is now available at [http://localhost:9090](http://localhost:9090).

Killing the stack requires a double `Ctrl+C`.

You may use Adminer to access the database using a convenient GUI available at [http://localhost:8080](http://localhost:8080). Use the following credentials:

- Server: `sti_db`
- Username: `sti`
- Password: `stipass`
- Database: `sti`

## Authors

Messenger is made by:

- Diluckshan RAVINDRANATHAN
- Eric NOËL
- Moïn DANAI