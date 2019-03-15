#!/usr/bin/env python
#-*- coding:utf-8 -*-

import MySQLdb
import time

DB_IP = 'localhost'
DB_NAME = 'waming_park_db'
DB_USER = 'root'
DB_PASSWD = 'frogshealth'
TB_NAME = 'park01'
#���ʱ��, ��ʱ����,���ڵ���,����ʱʱ��,
BILLING = '3,30,3,600'
HISTORY_TB_NAME = ''
HISTORY_HEAD = 'history'
MAXNUMBER_IN_TABLE=10

def mysql_connectdb():
    db = MySQLdb.connect(DB_IP, DB_USER, DB_PASSWD, DB_NAME, charset='gbk')
    db.autocommit(False)
    return db

def mysql_get_version():
    database = mysql_connectdb()
    cursor = database.cursor()
    try:
        cursor.execute('select version()')
        ret = cursor.fetchone()
        database.commit()
        return ret
    except:
        database.rollback()
    finally:
        cursor.close()
        database.close()

#���������Ƿ��ж�Ӧ��ͣ����Ϣ��o
#����ɾ�����ڵ���һ���������������Ȧû������ͬ������Ϣ.
#Ȼ���ѯ�����Ƿ���ȷ��ʻ��ģ�����û��ʻ���Ķ�Ӧ�ĳ�����Ϣ
#���û�еĻ��򽫱��ε���Ϣ�������
#Ȼ�󽫱�����Ϣ���뵽����
def mysql_updatedb_when_carin(list):
    db = mysql_connectdb()
    cursor = db.cursor()
    color = list[0]
    plate = list[1]
    intime = list[2]
    #ɾ�����ڵ�δȷ���������Ϣ
    #sql = 'delete from %s' % TB_NAME + ' where c3Color=\'%s\' and c12Plate=\'%s\' and bInOK=false' % (color, plate)
    sql = 'delete from %s' % TB_NAME + ' where bInOK=false'
    #print sql
    ret = False
    try:
        cursor.execute(sql)
        db.commit()
        #ɾ��ͬ���Ƶ�δȷ��ʻ����Ϣ
        sql = 'delete from %s where c3Color=\'%s\' and c12Plate=\'%s\' and bOutOK=false' % (TB_NAME, color, plate)
        cursor.execute(sql)
        db.commit()

        sql = 'select * from %s' % TB_NAME + ' where c3Color=\'%s\' and c12Plate=\'%s\' and OutTime is NULL' % (color, plate)
        #print sql
        cursor.execute(sql)
        result = cursor.fetchone()
        #����в�ѯ����¼����ô˵���ó������ӱܽ��ѵļ�¼�����ܷ���
        if not result:
            sql = 'insert into %s(c3Color,c12Plate,InTime,cInUpload)' % TB_NAME + ' values(\'%s\',\'%s\',\'%s\',\'N\')' % (color,plate,intime)
            #print sql
            cursor.execute(sql)
            db.commit()
            ret = True
    except:
        db.rollback()
    finally:
        cursor.close()
        db.close()
        return ret

#��ȡ����ͣ��ʱ��
import datetime
#�������⵽������Ϣ���ͻ��������ݿ���Ѱ��OutTimeΪNULL�Ķ�Ӧ������Ϣ�ļ�¼��
#����ҵ��˸�����¼���������OutTimeʱ��
#���û�ҵ������ճ�����Ϣ��OutTime��ʱ���������������OutTime��������Ѱ��
#����ʱ��ֵ��������Ϣ�ͱ���Ϊ��
def mysql_getparktime_when_carout(list):
    db = mysql_connectdb()
    cursor = db.cursor()
    color = list[0]
    plate = list[1]
    outtime = list[2]
#����Outtime Null�������������û����������¼������outtimeʱ������ȡ���µ�������¼
    sql = 'select * from %s' % TB_NAME + ' where c3Color=\'%s\' and c12Plate=\'%s\' and OutTime is NULL' % (color, plate)
    #print sql
    ret_list = []
    do_flag = False
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        sql = ''
        if result:
            intime = result[3]
            select_outtime = result[3]
            canparktime = result[8]
            sql = 'update %s' % TB_NAME + \
                  ' set OutTime=\'%s\',cOutUpload=\'N\' where c3Color=\'%s\' and c12Plate=\'%s\' and InTime=\'%s\'' % (outtime, color, plate, intime)
            do_flag = True
        else:
            #û�м�������Ϣ������ʱ�������������
            sql = 'select * from %s' % TB_NAME + ' where OutTime in (select max(OutTime) from %s' % TB_NAME + \
                   ' where c3Color=\'%s\' and c12Plate=\'%s\' order by OutTime)' % (color, plate)
            #print sql
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                intime = result[3]
                select_outtime = result[5]
                canparktime = result[8]
                do_flag = True
                sql = 'update %s' % TB_NAME + \
                      ' set OutTime=\'%s\',cOutUpload=\'N\' where c3Color=\'%s\' and c12Plate=\'%s\' and OutTime=\'%s\'' % (outtime, color, plate, select_outtime)
        if do_flag == True:
            #print sql
            cursor.execute(sql)
            db.commit()
            ret_list.append(intime)
            ret_list.append(outtime)
            ret_list.append(canparktime)
    except Exception as e:
        print '[except] mysql_getparktime_when_carout'
        print e.args
        db.rollback()
    finally:
        cursor.close()
        db.close()
        return ret_list

#def mysql_updatedb_when_carout(list):
#    db = mysql_connectdb()
#    cursor = db.cursor()
#    color = list[0]
#    plate = list[1]
#    outtime = list[2]
#    sql = 'select * from %s' % TB_NAME + ' where c3Color=\'%s\'' % color + ' and c12Plate=\'%s\'' % plate + ' and OutTime is NULL'
#    #print sql
#    ret = False
#    try:
#        cursor.execute(sql)
#        results = cursor.fetchone()
#        db.commit()
#        if not results:
#            print 'can\' find car park message'
#        else:
#            sql = 'update %s' % TB_NAME + ' set OutTime=\'%s\',cOutUpload=\'N\'' % outtime + ' where c3Color=\'%s\'' % color + ' and c12Plate=\'%s\'' % plate + ' and OutTime is NULL'
#            #print sql
#            try:
#                cursor.execute(sql)
#                db.commit()
#                ret = True
#            except:
#                db.rollback()
#    except Exception as e:
#        print 'mysql_updatedb_when_carout except'
#        print e.args
#        db.rollback()
#    finally:
#        cursor.close()
#        db.close()
#        return ret

#�����յ�����ʻ���ʻ���ĵظ���Ȧ���ź�ʱ
#����øú���������ʱ�������InTime��OutTime��Ӧ��������Ϣ
#��ʻ��ʻ��ȷ�ϱ�־Ϊtrue
def mysql_update_okflag(msglist):
    db = mysql_connectdb()
    cursor = db.cursor()
    msgtype = msglist[0]
    msgtime = msglist[1]
    try:
        if msgtype == 'InOK':
            select_msg = 'InTime'
            set_commont = 'bInOK'
            pos = 3
        else:
            select_msg = 'OutTime'
            set_commont = 'bOutOK'
            pos = 5
#��Ϊͣ����ֻ��һ����ڣ�����ֻ��ҪѰ�����µ�������Ϣ���ǵ�ǰ��������Ϣ
        sql = 'select * from %s' % TB_NAME + ' where %s' % select_msg + \
            ' in (select max(%s' %select_msg + ') from %s' % TB_NAME + ' order by %s)' %select_msg
        #print sql
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            timestamp = result[pos]
            sql = 'update %s' % TB_NAME + ' set %s' %set_commont + '=true where %s' % select_msg + '=\'%s\'' % timestamp
            #print sql
            cursor.execute(sql)
            db.commit()

            #Ѱ���ڱ���������Ϣ��ʱ��֮ǰ�ģ�δȷ��ʻ���ʻ������Ϣ����ɾ����
#            sql = 'select * from %s' % TB_NAME + ' where %s' % select_msg + ' < \'%s\'' % timestamp + ' and %s' %set_commont + '=False'
#            print sql
#            cursor.execute(sql)
#            result = cursor.fetchone()
#            if result:
#                timestamp = result[pos]
#                sql = 'delete from %s' % TB_NAME + ' where %s' % select_msg + '=\'%s\'' % timestamp
#                print sql
#                cursor.execute(sql)
#                db.commit()
            
    except Exception as e:
        print '[except] mysql_update_okflag'
        print e.args
        db.rollback()
    finally:
        cursor.close()
        db.close()

def mysql_update_leaveflag(msglist):
    db = mysql_connectdb()
    cursor = db.cursor()
    color = msglist[0]
    plate = msglist[1]
    intime = msglist[2]
    outtime = msglist[3]
    try:
        sql = 'update %s set cIsLeave=\'Y\' where c3Color=\'%s\' and c12Plate=\'%s\' and InTime=\'%s\' and OutTime=\'%s\'' % \
              (TB_NAME, color, plate, intime, outtime)
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print e.arg
    finally:
        cursor.close()
        db.close()

MAX_READ_LINE=5

#��ȡ���ݿ���û���ϴ�����Ϣ��Ŀ
#ÿ�������ȡMAX_READ_LINE����Ϣ����ֹ��Ϣ̫��ռ���ڴ�̫��
def mysql_get_noupload_item():
    db = mysql_connectdb()
    cursor = db.cursor()
    sql = 'select * from %s' % TB_NAME + ' where bInOK=true and cInUpload=\'N\' or cOutUpload=\'N\''
    #print sql
    item_list=[]
    try:
        cursor.execute(sql)
        #print cursor.rowcount
        if cursor.rowcount > MAX_READ_LINE:
            lines = MAX_READ_LINE
        else:
            lines = cursor.rowcount

        while lines > 0:
            results = cursor.fetchone()
            if results:
                color = results[0]
                plate = results[1]
                intime = results[3]
                outtime = results[5]
                in_flag = results[6]
                out_flag = results[7]

                if in_flag == 'N':
                    head = 'In'
                    if out_flag == 'N':
                        head = 'All'
                elif out_flag == 'N':
                    head = 'Out'
                else:
                    print '�����ж�'
                string = '%s,%s,%s,%s,%s' % (head,color,plate,intime,outtime)
                #print 'string=%s' % string
                item_list.append(string)
                lines = lines - 1
            else:
                break
    except Exception as e:
        db.rollback()
        print '[except] mysql_get_noupload_item'
        print e.args
    finally:
        cursor.close()
        db.close()
        return item_list

#����һ�����������ɺ�ͨ��restful�ṹ�����ϴ�
#�ϴ��ɹ�����Ϣ���뵽�ú�����Ϊ���
def mysql_update_uploadflag(string):
    db = mysql_connectdb()
    cursor = db.cursor()
    try:
        strlist = string.split(',')
        color = strlist[1]
        plate = strlist[2]
        intime = strlist[3]
        outtime = strlist[4]
#for val in strlist:
#               print val
        if strlist[0] == 'All':
            sql = 'update %s' % TB_NAME + ' set cInUpload=\'Y\',cOutUpload=\'Y\' \
                  where c3Color=\'%s\' and c12Plate=\'%s\' and InTime=\'%s\' and OutTime=\'%s\'' \
                  % (color, plate, intime, outtime)
        elif strlist[0] == 'In':
            sql = 'update %s' % TB_NAME + ' set cInUpload=\'Y\' \
                  where c3Color=\'%s\' and c12Plate=\'%s\' and InTime=\'%s\' and OutTime is NULL' \
                  % (color, plate, intime)
        elif strlist[0] == 'Out':
            sql = 'update %s' % TB_NAME + ' set cOutUpload=\'Y\' \
                  where c3Color=\'%s\' and c12Plate=\'%s\' and InTime=\'%s\' and OutTime=\'%s\'' \
                  % (color, plate, intime, outtime)
        else:
            print 'mysql_update_uploadflag error'
        #print sql
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print '[except]mysql_update_uploadflag'
        print e.args
        db.rollback()
    finally:
        cursor.close()
        db.close()
        
def mysql_get_complete_item():
    db = mysql_connectdb()
    cursor = db.cursor()
    ret_string_list = []
    try:
        sql = 'select * from %s' % TB_NAME + ' where cInUpload=\'Y\' and cOutUpload=\'Y\' and bInOK=true and bOutOK=true'
        cursor.execute(sql)
        lines = cursor.rowcount
        if lines > MAX_READ_LINE:
            lines = MAX_READ_LINE
        while lines > 0:
            result = cursor.fetchone()
            if result:
                ret_string_list.append(result)
            lines = lines - 1
    except Exception as e:
        print e.args
    finally:
        cursor.close()
        db.close()
        return ret_string_list

HISTORYTB_NAME = 'history20190101'


def create_history_table(datestring, db, cursor):
    ret = ''
    try:
        name = '%s%s' % (HISTORY_HEAD, datestring)
        sql = 'create table %s(c3Color char(3) default \'NN\',\
                c12Plate char(12) default \'NULL\',\
                bInOK tinyint(1) default false,\
                InTime datetime default NULL,\
                bOutOK tinyint(1) default false,\
                OutTime datetime default NULL,\
                cInUpload char(1) default \'O\',\
                cOutUpload char(1) default \'O\',\
                u32CanParkTime int(4) unsigned default 0,\
                cIsLeave char(1) default \'N\')' % name 

        cursor.execute(sql)
        db.commit()
        
        sql = 'alter table %s add index IndexMulColorPlate(c3Color(2),c12Plate(12))' % name
        cursor.execute(sql)
        db.commit()

        sql = 'alter table %s add index IndexMulCPIO(c3Color(2),c12Plate(12),InTime,OutTime)' % name
        cursor.execute(sql)
        db.commit()

        sql = 'alter table %s add index IndexUpload(cInUpload(1),cOutUpload(1))' % name
        cursor.execute(sql)
        db.commit()

        ret = name 
    except Exception as e:
        print e.args
        db.rollback()
    finally:
        return ret

def mysql_insert_item_into_histroytb(itemlist):
    global HISTORY_TB_NAME
    db = mysql_connectdb()
    cursor = db.cursor()
    ret_string_list = []
    numbers = 0
    try:
        #��ȡ������Ϣ����
        sql = 'select count(*) from %s' % HISTORY_TB_NAME
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            numbers = result[0]
        
        print 'numbers=%d,MAXNUMBER_IN_TABLE=%d' % (numbers, MAXNUMBER_IN_TABLE)
        #print 'itemlist=%s' % itemlist
        for item in itemlist:
#print 'item=%s'%item
            if numbers == MAXNUMBER_IN_TABLE: #���ݿ�����Ϣ��Ŀ�ﵽ�����ֵ,����һ���±����滻�ɱ�
                date = time.strftime('%Y%m%d', time.localtime(time.time()))
                ret = create_history_table(date, db, cursor)
                if ret:
                    HISTORY_TB_NAME = ret
            print 'HISTORY_TB_NAME:%s' % HISTORY_TB_NAME
            color = item[0]
            plate = item[1]
            intime = item[3]
            outtime = item[5]
            canparktime = item[8]
            sql = 'insert into %s' % HISTORY_TB_NAME \
                + '(c3Color, c12Plate, bInOK, InTime, bOutOK, OutTime, cInUpload, cOutUpload, u32CanParkTime)' \
                + ' values(\'%s\', \'%s\', true, \'%s\', true, \'%s\', \'Y\', \'Y\', %d)' % (color, plate, intime, outtime, canparktime)
#print sql
            cursor.execute(sql)
            db.commit()
            msg = '%s,%s,%s,%s' % (color, plate, intime, outtime)
            ret_string_list.append(msg)
            numbers = numbers + 1
    except Exception as e:
        db.rollback()
        print e.args
    finally:
        cursor.close()
        db.close()
        return ret_string_list

def mysql_remove_item_in_curtb(stringlist):
    db = mysql_connectdb()
    cursor = db.cursor()
    try:
        for string in stringlist:
            item = string.split(',')
            color = item[0]
            plate = item[1]
            intime = item[2]
            outtime = item[3]
            sql = 'delete from %s' % TB_NAME + ' where c3Color=\'%s\' and c12Plate=\'%s\' and InTime=\'%s\' and OutTime=\'%s\'' % \
                (color, plate, intime, outtime)
#print sql
            cursor.execute(sql)
            db.commit()
    except:
        db.rollback()
    finally:
        cursor.close()
        db.close()

def mysql_update_canparktime(string):
    db = mysql_connectdb()
    cursor = db.cursor()
    ret=False
    try:
        item = string.split(',')
        color = item[0]
        plate = item[1]
        time = item[2]
        #����ʱ��˳���ҵ����µ�һ����Ŀ
        sql = 'select * from %s where InTime in (select max(InTime) from %s  where c3Color=\'%s\' and c12Plate=\'%s\' order by InTime)' % \
              (TB_NAME, TB_NAME, color, plate)
        cursor.execute(sql)
        results = cursor.fetchone()
        if results:
            intime = results[3]
            sql = 'update %s set u32CanParkTime=%s where c3Color=\'%s\' and c12Plate=\'%s\' and InTime=\'%s\'' % \
                  (TB_NAME, time, color, plate, intime)
            #print sql
            cursor.execute(sql)
            db.commit()
            ret = True
    except Exception as e:
        db.rollback()
        print e.args
    finally:
        cursor.close()
        db.close()
        return ret

def mysql_init():
    global HISTORY_TB_NAME
    db = mysql_connectdb()
    cursor = db.cursor()
    try:
        sql = 'select count(*) tables, table_schema from information_schema.tables where table_schema=\'%s\' group by table_schema' % DB_NAME
#print sql
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            totalnum = result[0]
            sql = 'select table_name from information_schema.tables where table_schema=\'%s\' limit %d,1' % (DB_NAME,totalnum-2) # -1�����һ����-2�ǵ����ڶ�����
#            print sql
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                HISTORY_TB_NAME = result[0]
                print 'HISTORY_TB_NAME:%s' % HISTORY_TB_NAME

    except Exception as e:
        print e.args
        db.rollback()
    finally:
        cursor.close()
        db.close()

mysql_init()
