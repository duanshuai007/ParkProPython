#!/bin/sh

HOSTNAME="localhost"
PORT="0"
USERNAME="root"
PASSWORD="frogshealth"
DBNAME="waming_park_db"
TABLENAME="park01"

PREFIX="mysql -h${HOSTNAME}  -P${PORT}  -u${USERNAME} -p${PASSWORD}"

#创建数据库
sql="create database IF NOT EXISTS ${DBNAME} default charset gbk"
res=`${PREFIX} -e "${sql}" 2>&1`

#echo ${res}
echo ${res} | grep "ERROR"
if [ $? -eq 0 ]
then
    echo "create database[${DBNAME}] failed"
    exit
fi

#创建表
sql="create table ${TABLENAME}(\
     c3Color char(3) default 'NN',\
     c12Plate char(12) default 'NULL',\
     bInOK tinyint(1) default false,\
     InTime datetime default NULL,\
     bOutOK tinyint(1) default false,\
     OutTime datetime default NULL,\
     cInUpload char(1) default 'O',\
     cOutUpload char(1) default 'O',\
     u32CanParkTime int(4) unsigned default 0,\
     cIsLeave char(1) default 'N')"

res=`${PREFIX} ${DBNAME} -e "${sql}" 2>&1`

echo ${res}
echo ${res} | grep "ERROR" > /dev/null
if [ $? -ne 0 ]
then
    #为了支持中文，需要设置为gbk编码
    #    set_zifuji="alter table ${TABLENAME} change Color Color char(4) character set gbk"
    #    ${PREFIX} ${DBNAME} -e "${set_zifuji}" 2>&1
    #创建组合索引
    sql="alter table ${TABLENAME} add index IndexMulColorPlate(c3Color(2),c12Plate(12))"
    res=`${PREFIX} ${DBNAME} -e "${sql}" 2>&1`

    #echo ${res}
    echo ${res} | grep "ERROR" > /dev/null
    if [ $? -eq 0 ]
    then
        echo "set mulindex color plate failed\r\n"
        exit
    fi

    sql="alter table ${TABLENAME} add index IndexMulCPIO(c3Color(2),c12Plate(12),InTime,OutTime)"
    res=`${PREFIX} ${DBNAME} -e "${sql}" 2>&1`

    #echo ${res}
    echo ${res} | grep "ERROR" > /dev/null
    if [ $? -eq 0 ]
    then
        echo "set mulindex color plate intime outtime failed\r\n"
        exit
    fi


    sql="alter table ${TABLENAME} add index IndexUpload(cInUpload(1),cOutUpload(1))"
    res=`${PREFIX} ${DBNAME} -e "${sql}" 2>&1`

    #echo ${res}
    echo ${res} | grep "ERROR" > /dev/null
    if [ $? -eq 0 ]
    then
        echo "set upload index failed\r\n"
        exit
    fi

    echo "table[${TABLENAME} create success]"

else
    echo ${res} | grep "already exists" > /dev/null
    if [ $? -eq 0 ]
    then 
        echo table[${TABLENAME}] exists
    fi
    echo "create table[${TABLENAME}] failed"
    exit
fi 

sql="create table history20190101(\
     c3Color char(3) default 'NN',\
     c12Plate char(12) default 'NULL',\
     bInOK tinyint(1) default false,\
     InTime datetime default NULL,\
     bOutOK tinyint(1) default false,\
     OutTime datetime default NULL,\
     cInUpload char(1) default 'O',\
     cOutUpload char(1) default 'O',\
     u32CanParkTime int(4) unsigned default 0,\
     cIsLeave char(1) default 'N')"

res=`${PREFIX} ${DBNAME} -e "${sql}" 2>&1`
