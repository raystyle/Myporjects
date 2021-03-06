# coding: utf-8

from flask import render_template, request, session
from . import app
from login_require import login_required
import db
import json
from utils import util

display = util.Display()
display.display['assets'] = 'block'
dis = display.display

@app.route('/idc/')
@login_required
def idc():
    idc_columns = ['id', 'name', 'address', 'adminer', 'phone', 'cabinet_num', 'switch_num']
    idcs = db.get_list(idc_columns, 'idc')
    return render_template('assets/idc/idc.html', idcs=idcs, display = dis)


@app.route('/idcadd/', methods=['POST', 'GET'])
@login_required
def idcadd():
    if request.method == 'GET':
        return render_template('assets/idc/idcadd.html', display = dis)
    else:
        data = request.form.to_dict()
        util.WriteLog('infoLogger').warning('%s add idc %s' % (session['username'], data['name']))
        return json.dumps(db.create(data, 'idc'))


@app.route('/idcdelete/', methods=['POST'])
@login_required
def idcdelete():
    id = request.form.get('id')
    columns = ['id', 'name']
    where = "id=" + id
    idc = json.loads(db.get_one(columns, where, 'idc'))
    util.WriteLog('infoLogger').warning('%s delete idc %s' % (session['username'], idc['name']))
    return json.dumps(db.delete(where, 'idc'))


@app.route('/idcupdate/', methods=['POST', 'GET'])
@login_required
def idcupdate():
    idc_columns = ['id', 'name', 'address', 'adminer', 'phone', 'cabinet_num', 'switch_num']
    if request.method == 'GET':
        id = request.args.get('id')
        where = "id=" + id
        data = db.get_one(idc_columns, where, 'idc')
        return json.dumps(data)
    else:
        data = request.form.to_dict()
        for k,v in data.items():
            if v == '':
                return json.dumps({'code': 1, 'errmsg': '不能为空'})
        where = "id=" + data['id']
        util.WriteLog('infoLogger').warning('%s update idc_id %s' % (session['username'], data['id']))
        return json.dumps(db.update(data, where, 'idc'))


@app.route('/cabinet/')
@login_required
def cabinet():
    cabinet_columns = ['id', 'name', 'idc_id', 'bandwidth', 'money', 'agreement_date', 'u_num', 'server_num', 'switch_num']
    cabinets = db.get_list(cabinet_columns, 'cabinet')
    idc_columns = ['id', 'name']
    idcs = db.get_list(idc_columns, 'idc')
    idcs = dict((idc['id'],idc['name']) for idc in idcs)
    for cabinet in cabinets:
        if cabinet['idc_id'] in idcs.keys():
            cabinet['idc_id'] = idcs[cabinet['idc_id']]
    return render_template('assets/cabinet/cabinet.html', cabinets=cabinets, display = dis)


@app.route('/cabinetadd/', methods=['POST', 'GET'])
@login_required
def cabinetadd():
    if request.method == 'GET':
        idc_columns = ['id', 'name', 'address', 'adminer', 'phone', 'cabinet_num', 'switch_num']
        idcs = db.get_list(idc_columns, 'idc')
        idcinfo = []
        for idc in idcs:
            idcinfo.append({'id': idc['id'], 'name': idc['name']})
        return render_template('assets/cabinet/cabinetadd.html', idcinfo=idcinfo, display = dis)
    else:
        data = request.form.to_dict()
        util.WriteLog('infoLogger').warning('%s add cabinet %s' % (session['username'], data['name']))
        return json.dumps(db.create(data, 'cabinet'))


@app.route('/cabinetdelete/', methods=['POST'])
@login_required
def cabinetdelete():
    id = request.form.get('id')
    columns = ['id', 'name']
    where = 'id=' + id
    cabinet = json.loads(db.get_one(columns, where, 'cabinet'))
    util.WriteLog('infoLogger').warning('%s delete cabinet %s' % (session['username'], cabinet['name']))
    return json.dumps(db.delete(where, 'cabinet'))


@app.route('/idcinfo/')
@login_required
def idcinfo():
    columns = ['id', 'name']
    return json.dumps(db.get_list(columns, 'idc'))


@app.route('/cabinetupdate/', methods=['POST', 'GET'])
@login_required
def cabinetupdate():
    cabinet_columns = ['id', 'name', 'idc_id', 'bandwidth', 'money', 'u_num', 'server_num', 'switch_num']
    if request.method == 'GET':
        id = request.args.get('id')
        where = "id=" + id
        data = db.get_one(cabinet_columns, where, 'cabinet')
        return json.dumps(data)
    else:
        data = request.form.to_dict()
        for k,v in data.items():
            if v == '':
                return json.dumps({'code': 1, 'errmsg': '不能为空'})
        where = "id=" + data['id']
        columns = ['id', 'name']
        idcs = db.get_list(columns, 'idc')
        idcs = dict((idc['id'], idc['name']) for idc in idcs)
        for k, v in idcs.items():
            if data['idc_id'] == v:
                data['idc_id'] = k
        util.WriteLog('infoLogger').warning('%s update cabinet_id %s' % (session['username'], data['id']))
        return json.dumps(db.update(data, where, 'cabinet'))


@app.route('/server/')
@login_required
def server():
    server_columns = ['id', 'hostname', 'lan_ip', 'wan_ip', 'cpu', 'mem', 'disk', 'virtual_nums', 'virtual_names', 'idc_id', 'cabinet_id']
    servers = db.get_list(server_columns, 'server')
    cabinets = json.loads(cabinetinfo())
    idcs = json.loads(idcinfo())
    for server in servers:
        virtual_nums_columns = ['count(*)']
        where = 'server_id=' +  str(server['id'])
        virtual_nums = json.loads(db.get_one(virtual_nums_columns, where, 'virtuals'))['count(*)']
        server['virtual_nums'] = virtual_nums

        virtual_names_columns = ['qufu']
        try:
            x = json.loads(db.get_one(virtual_names_columns, where, 'virtuals'))
            if isinstance(x, dict):
                names = x['qufu']
            elif isinstance(x, list):
                virtual_names = [ ",".join(i) for i in json.loads(db.get_one(virtual_names_columns, where, 'virtuals'))]
                names = ",".join(virtual_names)
            else:
                print 'not correct type'
            server['virtual_names'] = names
        except BaseException,e:
            print e

        for cabinet in cabinets:
            if cabinet['id'] == server['cabinet_id']:
                server['cabinet_id'] = cabinet['name']

        for idc in idcs:
            if idc['id'] == server['idc_id']:
                server['idc_id'] = idc['name']
    return render_template('assets/server/server.html', servers=servers, display = dis)


@app.route('/cabinetinfo/')
@login_required
def cabinetinfo():
    cabinet_columns = ['id', 'name']
    return json.dumps(db.get_list(cabinet_columns, 'cabinet'))


@app.route('/serveradd/', methods=['POST', 'GET'])
@login_required
def serveradd():
    if request.method == 'GET':
        return render_template('assets/server/serveradd.html', display = dis)
    else:
        data = request.form.to_dict()
        util.WriteLog('infoLogger').warning('%s add server %s' % (session['username'], data['hostname']))
        return json.dumps(db.create(data, 'server'))


@app.route('/serverdelete/', methods=['POST'])
@login_required
def serverdelete():
    id = request.form.get('id')
    columns = ['id', 'hostname']
    where = 'id=' + id
    hostname = json.loads(db.get_one(columns, where, 'server'))
    util.WriteLog('infoLogger').warning('%s delete server hostname %s' % (session['username'], hostname['hostname']))
    return json.dumps(db.delete(where, 'server'))


@app.route('/serverupdate/', methods=['POST', 'GET'])
@login_required
def serverupdate():
    server_columns = ['id', 'hostname', 'lan_ip', 'wan_ip', 'cpu', 'mem', 'disk', 'virtual_nums', 'virtual_names', 'idc_id', 'cabinet_id']
    if request.method == 'GET':
        id = request.args.get('id')
        where = "id=" + id
        data = db.get_one(server_columns, where, 'server')
        return json.dumps(data)
    else:
        data = request.form.to_dict()
        for k,v in data.items():
            if v == '':
                return json.dumps({'code': 1, 'errmsg': '不能为空'})
        where = "id=" + data['id']
        util.WriteLog('infoLogger').warning('%s update server_id %s' % (session['username'], data['id']))
        return json.dumps(db.update(data, where, 'server'))


@app.route('/virtuals/')
@login_required
def virtuals():
    virtuals_columns = ['id', 'qufu', 'platform', 'serverid', 'hostname', 'lan_ip', 'wan_ip', 'cpu', 'mem', 'disk', 'master_slave', 'server_id']
    virtuals = db.get_list(virtuals_columns, 'virtuals')
    server_columns = ['id', 'hostname']
    servers = db.get_list(server_columns, 'server')
    servers = dict((server['id'], server['hostname']) for server in servers)
    for virtual in virtuals:
        if virtual['server_id'] in servers.keys():
            virtual['server_id'] = servers[virtual['server_id']]
    return render_template('assets/virtuals/virtuals.html', virtuals=virtuals, display = dis)


@app.route('/serverinfo/')
@login_required
def serverinfo():
    server_columns = ['id', 'hostname']
    serverinfo = db.get_list(server_columns, 'server')
    return json.dumps(serverinfo)


@app.route('/virtualadd/', methods=['POST', 'GET'])
@login_required
def virtualadd():
    if request.method == 'GET':
        return render_template('assets/virtuals/virtualadd.html', display = dis)
    else:
        data = request.form.to_dict()
        util.WriteLog('infoLogger').warning('%s add virtual %s' % (session['username'], data['hostname']))
        return json.dumps(db.create(data, 'virtuals'))


@app.route('/virtualdel/', methods=['POST'])
@login_required
def virtualdel():
    id = request.form.get('id')
    columns = ['id', 'hostname']
    where = "id=" + id
    hostname = json.loads(db.get_one(columns, where, 'virtuals'))
    util.WriteLog('infoLogger').warning('%s delete virtual hostname %s' % (session['username'], hostname['hostname']))
    return json.dumps(db.delete(where, 'virtuals'))


@app.route('/virtualupdate/', methods=['POST', 'GET'])
@login_required
def virtualupdate():
    if request.method == 'GET':
        columns = ['id', 'qufu', 'platform', 'serverid', 'hostname', 'lan_ip', 'wan_ip', 'cpu', 'mem', 'disk', 'master_slave', 'server_id']
        id = request.args.get('id')
        where = 'id=' + id
        virtual = db.get_one(columns, where, 'virtuals')
        return json.dumps(virtual)
    else:
        data = request.form.to_dict()
        for k,v in data.items():
            if v == '':
                return json.dumps({'code': 1, 'errmsg': '不能为空'})
        where = "id=" + data['id']
        util.WriteLog('infoLogger').warning('%s update virtual_id %s' % (session['username'], data['id']))
        return json.dumps(db.update(data, where, 'virtuals'))


@app.route('/inner/', methods=['POST', 'GET'])
@login_required
def inner():
    sql = "create table if not exists innerServer(" \
          "id int auto_increment PRIMARY key not null," \
          "hostname varchar(50) not null COMMENT 'hostname'," \
          "ip varchar(50) not null COMMENT 'ip'," \
          "cpu varchar(20) not null COMMENT 'cpu'," \
          "mem varchar(30) not null COMMENT '内存'," \
          "disk varchar(30) not null COMMENT '硬盘'," \
          "physicalHost varchar(30) COMMENT '宿主机'," \
          "user varchar(30) not null COMMENT '使用人') " \
          "ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8 COMMENT='内网服务器管理表'"
    db.createTable(sql)
    columns = ['id', 'hostname', 'ip', 'cpu', 'mem', 'disk', 'physicalHost', 'user']
    data = db.get_list(columns, 'innerServer')
    return render_template('assets/inner/inner.html', inners=data, display = dis)


@app.route('/inneradd/', methods=['POST', 'GET'])
@login_required
def inneradd():
    if request.method == 'GET':
        return render_template('assets/inner/inneradd.html')
    else:
        inner = request.form.to_dict()
        reason = db.create(inner, 'innerServer')
        return json.dumps(reason)


@app.route('/innerdel/', methods=['POST'])
@login_required
def innerdel():
    id = request.form.get('id')
    where = 'id=' + id
    reason = db.delete(where, 'innerServer')
    return json.dumps(reason)


@app.route('/innerUpdate/', methods=['POST', 'GET'])
@login_required
def innerUpdate():
    if request.method == 'GET':
        id = request.args.get('id')
        where = 'id=' + id
        columns = ['id', 'hostname', 'ip', 'cpu', 'mem', 'disk', 'physicalHost', 'user']
        data = db.get_one(columns, where, 'innerServer')
        return json.dumps(data)
    else:
        data = request.form.to_dict()
        id = data.pop('id')
        where = 'id=' + id
        reason = db.update(data, where, 'innerServer')
        return json.dumps(reason)


@app.route('/innerCopy/', methods=['POST', 'GET'])
@login_required
def innerCopy():
    return 111