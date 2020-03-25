from flask import abort
import MySQLdb
import db


def make_table_name(id):
    return 'table_' + id


check_table_cmd = '''select * from {};'''


def check_table_exists(id):
    conn = db.conn()
    cursor = conn.cursor()
    try:
        cursor.execute(check_table_cmd.format(make_table_name(id)))
    except Exception:
        return False

    return True


get_all_tables_cmd = '''select tableID, tableName from Tables;'''


def getAllTables():
    conn = db.conn()
    cursor = conn.cursor()

    cursor.execute(get_all_tables_cmd)
    return cursor.fetchall()


create_table_cmd = '''create table {} (id text);'''
insert_table_cmd = '''insert into Tables (tableName) VALUES (%s);'''
check_table_exists_cmd = '''select * from Tables where tableName = %s;'''


def createTable(tableName):
    conn = db.conn()
    cursor = conn.cursor()

    try:
        cursor.execute(check_table_exists_cmd, [tableName])
    except MySQLdb.IntegrityError:
        abort(400, 'This table already exists')

    try:
        cursor.execute(insert_table_cmd, [tableName])
        conn.commit()
    except Exception:
        abort(500, 'SQL error at insert table comand')

    tableId = cursor.lastrowid
    print(tableId)
