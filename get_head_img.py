import itchat
import os

itchat.auto_login(hotReload=True)
friends=itchat.get_friends()
for friend in friends:
    friend_head_img=itchat.get_head_img(userName=friend.get('UserName'))
    mypath=os.path.join(os.getcwd(),'好友头像')+'\\'+friend['NickName']+'.png'
    try:
        with open(mypath,'wb') as f:
            f.write(friend_head_img)
            print('"%s"的头像已保存' % friend['NickName'])
    except Exception as e:
        print(e)
