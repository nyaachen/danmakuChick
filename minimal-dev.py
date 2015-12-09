# coding=utf-8
# This version is not supporting anymore.
# destribute 2015.12.09 04:36 
# 真的会有人打开来看一眼吗  
# 写在公开之前的话  
# 
# bilibili弹幕鸡-开发者简版  
# 
# 开发： 橙橙喵  
# 叫做简版是因为和官方版本相比功能有限 
# 运行平台为Python 2.7 
# 不知道如何执行的话，请百度一下Python 
# 要连接到你自己的直播间，记得改下面的参数 
# 这一版本已经停止开发，请等待新版本  
# 虽然如此，但仍然正常工作，麻雀虽小，五脏俱全  

import socket
import logging
import time
from multiprocessing import Process
import json
from binascii import a2b_hex, b2a_hex

# 要用这个最小客户端连接到你的直播间，就把这个数字改掉， 
# 请注意闪耀之星活动的奖励短号无效 
roomid=10101
# 只能是数字，包含字母会报错 

# 下面的代码既包含功能组成部分，也包含格式控制部分 
# 我做了一些格式控制 看起来好看一点  
# 如果你想要修改代码，那么你可以进行修改,但请声明你发布的是修改版本  

#2015.12.09 04:55 更新了由于字符编码所导致的问题  
#2015.12.10 00:02 更新了由于字符编码所导致的问题  


# livebilibili danmaku server
danmakuServer, danmakuServerPort = 'livecmt-1.bilibili.com', 88
# default value for a heart beat info
heartBeat = '\x01\x02\x00\x04'      # \x0102 is heartbeat and \x0004 is len()
# time to sleep between two heart beat
sleepTime = 40.0                    # The value in copyliu's one is 60 sec
# default value for establish a connection
establishHeader, liveRoomID, currentUserUID = '\x01\x01\x00\x0c', a2b_hex('{:0>8}'.format('{:x}'.format(roomid))), '\x00\x00\x00\x00'


# HeartBeat to keep connection & get info
def sendHeartBeat(socketClient, heartBeatText, timeToSleep):
    while 1:
        try :
            socketClient.send(heartBeatText)
            logging.info('HeartBeat send.')
            logging.debug('HeartBeat is' + heartBeatText)
            time.sleep(timeToSleep)
        except Exception :
            logging.warning('HeartBeat send fail!')


# default json part dealing
def msgOut(message):
    ''' msgOut( <json data> ) try to output sth. '''

    packet = json.loads(message)
    if packet['cmd'] == 'DANMU_MSG':
        logging.info("A Danmaku message!")
        if packet['info'][2][2] == 1:
            print u"管",
        if packet['info'][2][3] == '1':
            print u"爷",
        if not len(packet['info'][3]) == 0:
            print u'【', packet['info'][3][1], packet['info'][3][0], u'】',
        print packet['info'][2][1], u'说：', packet['info'][1]
    elif packet['cmd'] == 'SEND_GIFT':
        print u'******', packet['data']['uname'], packet['data']['action'],
        print packet['data']['giftName'], 'X', packet['data']['num'], u'******'
    elif packet['cmd'] == 'SYS_GIFT':
        print u'{:*^60}'.format(packet['msg'])
    elif packet['cmd'] == 'SYS_MSG':
        print u'{:*^60}'.format(packet['msg'])
    elif packet['cmd'] == 'ROOM_BLOCK_MSG':
        print u'{:*^60}'.format(packet['uname'] + u'被禁言')
    elif packet['cmd'] == 'ROOM_ADMINS':
        pass
    elif packet['cmd'] == 'SEND_TOP':
        print u'{:*^60}'.format(u'礼物排行榜发生变化')
        for r in packet['data']['top_list']:
            print u'{0:@^40}{1:<20}'.format(r['uname'], r['coin'])
    elif packet['cmd'] == 'BET_START':
        print u"******当前房间进行的竟猜：", packet['data']['data']['bet']['question'], u'******'
        print u"********A****{:*<40}".format(packet['data']['data']['bet']['a'])
        print u"********B****{:*<40}".format(packet['data']['data']['bet']['a'])
    elif packet['cmd'] == 'BET_RANKER':
        pass
    elif packet['cmd'] == 'BET_BETTOR':
        pass
    elif packet['cmd'] == 'BET_BANKER':
        pass
    elif packet['cmd'] == 'BET_END':
        pass
    elif packet['cmd'] == 'WELCOME':
        logging.info("A welcome message!")
        print u'**********欢迎{}进入直播间**********'.format(packet['data']['uname'])
    elif packet['cmd'] == 'LIVE':
        pass
    elif packet['cmd'] == 'ROOM_AUDIT':
        pass
    else:
        logging.warning(u'接收到未定义的数据包')
        logging.warning(message)

print u'Connect to chatroom #', roomid
danmakuClient = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
danmakuClient.connect((danmakuServer, danmakuServerPort))
danmakuClient.send(establishHeader + liveRoomID + currentUserUID)
heartBeatSendingProcess = Process(target=sendHeartBeat, args=(danmakuClient, heartBeat, sleepTime,))
heartBeatSendingProcess.start()
try :
    while 1:
        data = danmakuClient.recv(1)
        if not data :
            # Warning Connection Broken
            raise IOError
        msgtype = int(b2a_hex(danmakuClient.recv(1)),16)
        if msgtype in [1]:
            msginfo = danmakuClient.recv(4)
            pass
        elif msgtype in [2, 4]:
            msglen = int(b2a_hex(danmakuClient.recv(2)),16)
            msgvalue = danmakuClient.recv(msglen-4)
            msgOut(msgvalue)
        elif msgtype in [8]:
            msginfo = danmakuClient.recv(2)
            pass
        elif msgtype in [17]:
            pass
        else :
            msglen = int(b2a_hex(danmakuClient.recv(2)), 16)
            msgvalue = danmakuClient.recv(msglen-4)
except KeyboardInterrupt:
    print u'KBD INTERRUPT'
    raise
finally :
    danmakuClient.close()
    heartBeatSendingProcess.terminate()
