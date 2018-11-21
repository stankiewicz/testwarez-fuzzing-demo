#!flask/bin/python


import collections
import os
import sqlite3
from functools import wraps

from flask import Flask, make_response, json
from flask import g
from flask import request
from flask_restful import Resource, Api
from flask.json import dumps

app = Flask(__name__, static_url_path="")

api = Api(app)

DATABASE = 'pet_store.db'


def connect_db():
    return sqlite3.connect(DATABASE)


@app.before_request
def before_request():
    g.sqlitedb = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'sqlitedb'):
        g.sqlitedb.close()


def get_sqlitedb():
    db = getattr(g, 'sqlitedb', None)
    if db is None:
        db = g.sqlitedb = connect_db()
    return db


def query_sqlitedb(query, args=(), one=False):
    cur = get_sqlitedb().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def init_sqlite():
    with app.app_context():
        db = get_sqlitedb()
        cur = db.cursor().execute('''CREATE TABLE  IF NOT EXISTS  pets
             (breed TEXT, id INT, name TEXT, tag TEXT)''')
        cur = db.cursor().execute('''DELETE FROM pets''')
        cur = db.cursor().execute('''INSERT INTO pets VALUES ('husky',123,'Pete','white')''')

        db.commit()



def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp

        return decorated_function

    return decorator


def add_security_headers(f):
    return add_response_headers(
        {
            'X-Content-Type-Options': 'nosniff',
            'strict-transport-security': 'max-age=631138519; includeSubDomains;'
        }
    )(f)


def etree_to_dict(t):
    d = {t.tag: map(etree_to_dict, t.iterchildren())}
    d.update(('@' + k, v) for k, v in t.attrib.iteritems())
    d['text'] = t.text
    return d


@app.route('/api/pet/<pet_id>', methods=['PUT'])
def pet_put(pet_id):
    pet = json.loads(request.data)
    db = get_sqlitedb()
    cur = db.cursor()
    sql = "UPDATE pets SET breed='" + pet['breed'] + "',name='" + pet['name'] + "',tag='" + pet[
        'tag'] + "' where id=" + str(pet_id)
    cur.execute(sql)
    db.commit()
    resp = make_response('ok')
    return resp, 200


@app.route('/api/pet', methods=['POST'])
def pet_post():
    pet = {}
    if request.headers['Content-Type'] == 'application/xml':
        from lxml import etree
        x = etree.fromstring(request.data)
        d = etree_to_dict(x)
        pet['breed'] = d['pet'][0]['text']
        pet['id'] = d['pet'][1]['text']
        pet['name'] = d['pet'][2]['text']
        pet['tag'] = d['pet'][3]['text']
    elif request.headers['Content-Type'] == 'application/json':
        pet = request.json
    else:
        return 'Unsupported Media Type', 415
    db = get_sqlitedb()
    cur = db.cursor()
    sql = "INSERT INTO pets VALUES ('" + pet['breed'] + "'," + str(pet['id']) + ",'" + pet['name'] + "','" + pet[
        'tag'] + "')"
    print '###', sql
    cur.execute(sql)
    db.commit()
    resp = make_response('ok')
    return resp, 201
    pass

@app.route('/api/pet/<pet_id>', methods=['GET'])
def pet_get(pet_id):
    sql = "SELECT id,breed,name,tag  from pets where id=" + str(pet_id)
    print '#####',sql
    rows = query_sqlitedb(sql)
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['breed'] = row[1]
        d['name'] = row[2]
        d['tag'] = row[3]
        objects_list.append(d)
    resp = make_response(dumps(objects_list))
    resp.mimetype = "application/json"
    return resp, 200


@app.route('/api/pets', methods=['GET'])
def pets_get():
    sql = 'SELECT id,breed,name,tag  from pets'
    rows = query_sqlitedb(sql)
    objects_list = []
    for row in rows:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['breed'] = row[1]
        d['name'] = row[2]
        d['tag'] = row[3]
        objects_list.append(d)
    resp = make_response(dumps(objects_list))
    resp.mimetype = "application/json"
    return resp, 200


@app.route('/', methods=['GET'])
@add_security_headers
def index():
    return 'OK', 200


init_sqlite()
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
