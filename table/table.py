from flask import Blueprint, jsonify, request, abort, g, send_file

import table.db as db
import auth
import auth.jwt
import auth.perms
import uuid
import message
import csv
import os

table = Blueprint('table', __name__)


@table.route('/all', methods=['POST'])
@auth.login_required(perms=[8])
def allTables():
    tables = db.getAllTables()
    return jsonify(tables)


@table.route('/create', methods=['POST'])
@auth.login_required(perms=[9])
def createTable():
    data = request.get_json()

    if 'tableName' not in data or 'columns' not in data:
        abort(400, 'missing tableName or columns')

    for col in data['columns']:
        if '(' in col or ')' in col or ' ' in col:
            abort(400, 'Illegal column name')

    table_id = db.createTable(data['tableName'])

    for c in data['columns']:
        db.addColumn_id(table_id, c, g.userId)

    return 'success'


@table.route('/delete', methods=['POST'])
@auth.login_required(perms=[9])
def deleteTable():
    data = request.get_json()

    if 'tableId' not in data:
        abort(400, 'Missing tableId')

    db.delete_table(data['tableId'])
    return 'success'


@table.route('/addColumn', methods=['POST'])
@auth.login_required(perms=[9])
def addColumn():
    data = request.get_json()

    if 'tableId' not in data or 'columnName' not in data:
        abort(400, 'Missing tableId or columnName')

    if not db.checkTableExists(data['tableId']):
        abort(400, 'This table does not exist')

    if '(' in data['columnName'] or ')' in data['columnName'] or ' ' in data['columnName']:
        abort(400, 'Illegal column name')

    column = data['columnName'].strip()
    column = column.replace('`', '')
    db.addColumn_id(data['tableId'], column, g.userId)

    return 'success'


@table.route('/deleteColumn', methods=['POST'])
@auth.login_required(perms=[9])
def deleteColumn():
    data = request.get_json()

    if 'tableId' not in data or 'columnName' not in data:
        abort(400, 'Missing tableId or columnName')

    if not db.checkTableExists(data['tableId']):
        abort(400, 'This table does not exist')

    column = data['columnName'].strip()
    db.removeColumn(data['tableId'], column, g.userId)

    return 'success'


@table.route('/modifyColumn', methods=['POST'])
@auth.login_required(perms=[9])
def modifyColumn():
    data = request.get_json()

    if 'tableId' not in data or 'originalColumn' not in data or 'newColumn' not in data:
        abort(400, 'Missing tableId, originalColumn or newColumn')

    if not db.checkTableExists(data['tableId']):
        abort(400, 'This table does not exist')

    if '(' in data['newColumn'] or ')' in data['newColumn'] or ' ' in data['newColumn']:
        abort(400, 'Illegal column name')

    oldCol = data['originalColumn'].strip()
    newCol = data['newColumn'].strip()
    db.modifyColumn(data['tableId'], oldCol, newCol, g.userId)

    return 'success'


@table.route('/columns', methods=['POST'])
@auth.login_required(perms=[9])
def getCols():
    data = request.get_json()

    if 'tableId' not in data:
        abort(400, 'tableId not in request')

    if not db.checkTableExists(data['tableId']):
        abort(400, "This table does not exist")

    return jsonify(db.getColumns(data['tableId']))


@table.route('/modifyTableName', methods=['POST'])
@auth.login_required(perms=[9])
def modifyTableName():
    data = request.get_json()

    if 'tableId' not in data or 'name' not in data:
        abort(400, 'tableId or name not in request')

    if '(' in data['name'] or ')' in data['name']:
        abort(400, 'Illegal table name')

    db.modifyTableName(data['tableId'], data['name'], g.userId)

    return 'success'


@table.route('/addEntry', methods=['POST'])
@auth.login_required(perms=[10])
def addEntry():
    data = request.get_json()
    data['userId'] = g.userId

    if 'tableId' not in data or 'contents' not in data:
        abort(400, 'Missing tableId')
    
    db.addEntry(data)

    return jsonify()


@table.route('/removeEntry', methods=['POST'])
@auth.login_required(perms=[10])
def removeEntry():
    data = request.get_json()

    if 'tableId' not in data or 'id' not in data:
        abort(400, 'Missing tableID or iD')
    
    db.removeEntry(data['tableId'], data['id'], g.userId)

    return jsonify()


@table.route('/view', methods=['POST'])
@auth.login_required(perms=[8])
def viewTable():
    data = request.get_json()

    if 'tableId' not in data:
        abort(400, 'Missing tableId')

    return jsonify(db.viewTable(data['tableId']))


@table.route('/modifyEntry', methods=['POST'])
@auth.login_required(perms=[10])
def modifyEntry():
    data = request.get_json()
    data['userId'] = g.userId
    
    if 'tableId' not in data or 'contents' not in data:
        abort(400, 'Missing data')

    db.modifyEntry(data)
    
    return jsonify()


@table.route('/export', methods=['POST'])
@auth.login_required(perms=[8])
def export():
    data = request.get_json()

    if 'tableId' not in data:
        abort(400, 'Missing table ID')
    
    res = db.viewTable(data['tableId'])

    with open('table.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
        for row in res:
            print(row)
            writer.writerow(row)

    return send_file("table.csv", as_attachment=True)


@table.route('/track', methods=['POST'])
@auth.login_required(perms=[9])
def track():
    data = request.get_json()
    if 'tableId' not in data:
        abort(400, 'Missing table ID')
    
    db.track(data['tableId'])

    return jsonify()


@table.route('/untrack', methods=['POST'])
@auth.login_required(perms=[9])
def untrack():
    data = request.get_json()
    if 'tableId' not in data:
        abort(400, 'Missing table ID')
    
    db.untrack(data['tableId'])

    return jsonify()


@table.route('/itemHistory', methods=['POST'])
@auth.login_required(perms=[8])
def itemHistory():
    data = request.get_json()
    if 'tableId' not in data or 'id' not in data:
        abort(400, 'Missing ID')
    
    res = db.itemHistory(int(data['tableId']), int(data['id']))
    resp = []

    for row in res:
        json = {}
        json['value'] = row[4]
        json['time'] = row[6]
        json['type'] = row[7]
        resp.append(json)    

    return jsonify(resp)


@table.route('/tableHistory', methods=['POST'])
@auth.login_required(perms=[8])
def history():
    data = request.get_json()
    if 'tableId' not in data:
        abort(400, 'Missing table ID')
    
    res = db.history(int(data['tableId']))
    resp = []

    for row in res:
        json = {}
        json['type'] = row[7]
        json['time'] = row[6]

        if row[7] in [0, 3, 6]:
            json['value'] = row[3] + ' was changed to ' + row[4]
        if row[7] in [1, 4]:
            json['value'] = row[4] + ' was added'
        if row[7] in [2, 5]:
            json['value'] = row[3] + ' was removed'

        resp.append(json)
    
    return jsonify(resp)
