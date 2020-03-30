import itchat
import pymysql
import re
import time


#判断表是否存在，如果不存在就创建
def is_exitst_table():
    try:
        sql1='''create table if not exists wx_friend_chat_record(
                    user_name VARCHAR(255),
                    date_time VARCHAR(255),
                    content LongText
        )'''
        sql2 = '''create table if not exists wx_group_chat_record(
                        room_name VARCHAR(255),
                        user_name VARCHAR(255),
                        date_time VARCHAR(255),
                        content LongText
           )'''
        cursor.execute(sql1)
        cursor.execute(sql2)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()



def insert_friend_chat_record(user_name,date_time,content):
    try:
        sql='insert into wx_friend_chat_record values("%s","%s","%s")' \
            %(user_name,date_time,content)
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()


def insert_group_chat_record(room_name,user_name,date_time,content):
    try:
        sql='insert into wx_group_chat_record values("%s","%s","%s","%s")' \
            %(room_name,user_name,date_time,content)
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        if "for column 'room_name'" in str(e):
            try:
                sql = 'insert into wx_group_chat_record values("%s","%s","%s","%s")' \
                      % ("群未命名", user_name, date_time, content)
                cursor.execute(sql)
                db.commit()
            except Exception as e:
                print(e)
                db.rollback()
        else:
            db.rollback()


@itchat.msg_register(['Text'])
def friend_chat_record(msg):
    try:
        insert_friend_chat_record(
            user_name=comp.sub('',msg.User['NickName']),
            date_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
            content=comp.sub('',msg['Text'])
        )
    except Exception as e:
        print(e)


@itchat.msg_register(['Text'],isGroupChat=True)
def group_chat_record(msg):
    try:
        if msg['ActualNickName']:
            user_name=msg['ActualNickName']
        else:
            user_name="不可不信缘"
        insert_group_chat_record(
            room_name=comp.sub('',msg.User['NickName']),
            user_name=comp.sub('',user_name),
            date_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),
            content=comp.sub('',msg['Text'])
        )
    except Exception as e:
        print(e)



if __name__=='__main__':
    db=pymysql.connect('localhost','root','123','zms')
    cursor=db.cursor()
    is_exitst_table()
    comp = re.compile(r'\'|"')
    itchat.auto_login(hotReload=True)
    itchat.run()