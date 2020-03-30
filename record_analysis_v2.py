from pyecharts import options
from pyecharts.charts import Bar
import pandas as pd
import numpy
import pymysql
import time
import jieba
from wordcloud import WordCloud
import PIL.Image

#读取数据库的微信聊天信息
def get_data():
    db=pymysql.connect(host='localhost',user='root',password='123',database='zms',port=3306)
    cursor=db.cursor()
    friend_record_data=pd.read_sql("select * from wx_friend_chat_record",con=db)
    group_record_data=pd.read_sql("select * from wx_group_chat_record",con=db)
    return (friend_record_data,group_record_data)

#获取群记录的最小和最大时间
def get_min_max_time():
    group_record_data['date_time'] = pd.to_datetime(group_record_data['date_time'])
    all_min_time = str(group_record_data['date_time'].min())
    all_max_time = str(group_record_data['date_time'].max())
    return (all_min_time,all_max_time)

#获取房间列表
def get_rooms():
    rooms=list(set(group_record_data['room_name']))
    return rooms

#群记录数据分析
#绘制群活跃度
def room_active_level():
    group_record_total=group_record_data['room_name'].value_counts()
    group_name_list=list(group_record_total.index)
    group_record_list=list(group_record_total)
    c=(
        Bar()
        .add_xaxis(group_name_list)
        .add_yaxis('消息条数',group_record_list)
        .set_global_opts(
            title_opts=options.TitleOpts(title="群活跃情况",subtitle=all_min_time+"\n"+all_max_time),
            xaxis_opts=options.AxisOpts(axislabel_opts=options.LabelOpts(rotate=-15))
            )
        # .reversal_axis()

    )
    c.render("群活跃情况.html")

# 绘制各群话痨前20强
def room_user_active_level(room_name):
    target_room=group_record_data[group_record_data['room_name']==room_name]
    user_record=target_room['user_name'].value_counts(ascending=True)
    height=str(min(max(user_record.count()*35,350),700))+"px"
    c=(
        Bar(init_opts=options.InitOpts(height=height,width="1000px"))
        .add_xaxis(list(user_record.index)[-20:])
        .add_yaxis('发送条数',list(user_record)[-20:],label_opts=options.LabelOpts(position="right"))
        .reversal_axis()
        .set_global_opts(
            title_opts=options.TitleOpts(title=room_name+"群话痨前20强",subtitle=all_min_time+"\n"+all_max_time),
        )

    )
    c.render(room_name+'群话痨前20强.html')

def my_word_cloud(room_name):
    content=group_record_data[group_record_data['room_name']==room_name]['content']
    contents=''.join(content)
    words=jieba.cut(contents)
    if len(contents)>=1000:
        text=' '.join(words)
        mask=numpy.array(PIL.Image.open('man.jpg'))
        word_cloud=WordCloud(
            background_color='white',
            width=600,
            height=600,
            font_path='FZLTXIHK.TTF',
            max_words=500,
            max_font_size=50,
            mask=mask
        ).generate(text)
        WordCloud.to_image(word_cloud).save(room_name+'.png')
    else:
        return


if __name__=='__main__':
    #每60秒自动刷新
    while True:
        friend_record_data,group_record_data=get_data()
        all_min_time,all_max_time=get_min_max_time()
        #绘制群活跃度
        room_active_level()
        #循环绘制各群话痨前20强
        for room_name in get_rooms():
            room_user_active_level(room_name)
            my_word_cloud(room_name)
        print('刷新时间:' + time.strftime("%Y-%m-%d %X", time.localtime()))
        time.sleep(60)
