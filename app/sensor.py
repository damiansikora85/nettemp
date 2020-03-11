from app import app
from flask import Flask, request, jsonify, g
import sqlite3
import os
import json
from random import randint
from flask_jwt_extended import jwt_required
import datetime

def get_db(rom):
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(rom)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def check_value(value, type, rom):
  adj=''
  tm=''
  value=float(value)
  conn = sqlite3.connect(app.db)
  c = conn.cursor()
  sql = ''' SELECT adj, tmp FROM sensors WHERE rom=? '''
  c.execute(sql, [rom])
  sensor=c.fetchall()
  for adj, tmp in sensor:
    tmp=float(tmp)
    adj=float(adj)
  msg=[]
  sql = ''' SELECT min, max, value1, value2, value3 FROM types WHERE type=? '''
  c.execute(sql, [type])
  list=c.fetchall()
  msg.append("IN VALUE: %f" % value)
  msg.append(list)
  conn.close()

  if adj:
    value=float(value)+(adj)
    msg.append("ADJ: %d" % value)
  for min, max, v1, v2, v3 in list:
    if (value>=float(min)) and (value<=float(max)): 
      if(value==v1) or (value==v2) or (value==v3):
        msg.append("filter 2 back to previous %f" % tmp)
        value=tmp
      else:
        value=float(value)
    else:
      msg.append("filter 1 back to previous %f" % tmp)
      value=tmp

  msg.append("VALUE OUT: %f" % value)
  print(msg)
  return value


def new_db(rom):
  rom = rom+'.sql'
  conn = sqlite3.connect(app.romdir+rom)
  c = conn.cursor()
  c.execute(''' SELECT count() FROM sqlite_master WHERE type='table' AND name='def' ''')
  if c.fetchone()[0]==1:
    print ("Database %s exists" %rom)
    return True
  else:
    with app.app_context():
      db = get_db(app.romdir+rom)
      with app.open_resource('schema/sensors_db_schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()
    print ("Database %s created" %rom)
    return False

def insert_db(rom,value):
  rom = rom+'.sql'
  conn = sqlite3.connect(app.romdir+rom)
  c = conn.cursor()
  c.execute(''' SELECT count() FROM sqlite_master WHERE type='table' AND name='def' ''')
  if c.fetchone()[0]==1:
    data = [value]
    sql = '''INSERT OR IGNORE INTO def (value) VALUES (?)'''
    c.execute(sql, data)
    conn.commit()
    conn.close()
    print ("Database %s insert ok" %rom)
    return True
  else:
    print ("Database %s not exist" %rom)
    return False

def update_sensor_tmp(rom,value):
  conn = sqlite3.connect(app.db)
  c = conn.cursor()
  rom1 = [rom]
  c.execute("SELECT count() FROM sensors WHERE rom=?", rom1)
  if c.fetchone()[0]==1:
    if int(datetime.datetime.now().strftime("%M"))%5==0:
      tmp_5ago=value
      sql = '''UPDATE sensors SET tmp=?, tmp_5ago=?, nodata='', time=datetime(CURRENT_TIMESTAMP, 'localtime') WHERE rom=?'''
      data = [value,tmp_5ago,rom]
    else:
      sql = '''UPDATE sensors SET tmp=?, nodata='', time=datetime(CURRENT_TIMESTAMP, 'localtime') WHERE rom=?'''
      data = [value,rom]
    c.execute(sql, data)
    # stat min max
    data = [value, value, rom]
    sql = '''UPDATE sensors SET stat_min=?, stat_min_time=datetime(CURRENT_TIMESTAMP, 'localtime') WHERE (stat_min>? OR stat_min is null OR stat_min='0.0') AND rom=?'''
    c.execute(sql, data)
    sql = '''UPDATE sensors SET stat_max=?, stat_max_time=datetime(CURRENT_TIMESTAMP, 'localtime') WHERE (stat_max<? OR stat_max is null OR stat_max='0.0') AND rom=?'''
    c.execute(sql, data)
    conn.commit()
    conn.close()
    print ("Sensor %s updated" %rom)
    return True
  else:
    print ("Sensor %s not exist" %rom)
    return False

def delete_db(rom):
  rom=rom+'.sql'
  if os.path.isfile(app.romdir+rom):
    os.remove(rom)
    print ("Database %s deleted" %rom)
    return True
  else:
    print ("Database %s not exist" %rom)
    return False

def delete_sensor(id,rom):
  data = [id, rom]
  conn = sqlite3.connect(app.db)
  c = conn.cursor()
  c.execute("DELETE FROM sensors WHERE id=? AND rom=?", data)
  conn.commit()
  conn.close()
  delete_db(rom)
  print ("Sensor %s removed ok" %rom)

def create_sensor(rom, data, data2, map_settings):
  conn = sqlite3.connect(app.db)
  c = conn.cursor()
  rom1 = [rom]
  c.execute("SELECT count() FROM sensors WHERE rom=?", rom1)
  if c.fetchone()[0]==0:
    sql = '''INSERT INTO sensors (rom,type,device,ip,gpio,i2c,usb,name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
    c.execute(sql, data)
    sql2 = '''UPDATE sensors SET alarm='off', adj='0', charts='on', status='on', ch_group=?, tmp_min='0', tmp_max='0', minmax='off', stat_min='0', stat_max='0', tmp_5ago='0', fiveago='on', map_id=? WHERE rom=?'''
    c.execute(sql2, data2)
    map = ''' INSERT OR IGNORE INTO maps (type, pos_x, pos_y, map_on, map_id, display_name) VALUES (?,?,?,?,?,?) '''
    c.execute(map, map_settings)
    conn.commit()
    conn.close()
    print ("Sensor %s added ok" %rom)
  else:
    print ("Sensor %s already exist" %rom)
  return None

def sensor():
    json = request.get_json()

    rom = None 
    if 'rom' in json: 
      rom=json['rom']

    type = None 
    if 'type' in json: 
      type=json['type']

    device = None 
    if 'device' in json: 
      device=json['device']

    ip = None 
    if 'ip' in json: 
      ip = json['ip']

    gpio = None 
    if 'gpio' in json: 
      gpio=json['gpio']

    i2c = None 
    if 'i2c' in json: 
      i2c=json['i2c']

    usb = None 
    if 'usb' in json: 
      usb=json['usb']

    name = randint(1000,9000)
    if 'name' in json: 
      name=json['name']
      if not json['name']:
        name = randint(1000,9000)

    tmp = None 
    if 'tmp' in json: 
      tmp=json['tmp']

    value = None 
    if 'value' in json: 
      value=json['value']
    
    group = type 
    if 'group' in json: 
      group=json['group']

    map_id = randint(1000,9000)
    map_y = randint(50,600)
    map_x = randint(50,600)
    data = [rom, type, device, ip, gpio, i2c, usb, name]
    data2 = [group, map_id, rom]
    map_settings = [type, map_y, map_x, 'on', map_id, 'on']
    value=check_value(value, type, rom)


    if insert_db(rom, value) == False:
      new_db(rom)
      insert_db(rom,value)

    if update_sensor_tmp(rom,value) == False:
      create_sensor(rom,data,data2,map_settings)
      update_sensor_tmp(rom,value)


@app.route('/sensor', methods=['POST'])
@jwt_required
def url_sensor():
  sensor()
  return '', 200


@app.route('/local', methods=['POST'])
def url_localhost():
  if request.remote_addr == '127.0.0.1':
    sensor()
    return 'Local'
  else:
    return '', 404

