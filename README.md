# Face Recognition

- Based on [face_recognition](https://github.com/ageitgey/face_recognition)
- A face recognition with [PostgreSQL](https://www.postgresql.org/)

## Installation

- Install Python 3.7.x
- Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Python dependencies

```bash
pip install face_recognition numpy opencv-python argparse psycopg2 prettytable
```

Install Postgres

- Using [Docker](https://hub.docker.com/_/postgres)
- Or install [PostgreSQL](https://www.postgresql.org/)

demo_video.py requires Pillow

```bash
pip install Pillow
```

## Setup

### Setup config file

- Create and edit config.json following config_template.json

### Setup Database

- Setup user and database in PostgreSQL
- Run the following command to create tables

```bash
python db_tool.py --cmd 'clean_db'
```

### Database tools

- A set of commands to access or update data in database

```bash
python db_tool.py --cmd 'summary'
```
```bash
python db_tool.py --cmd 'status'
```
