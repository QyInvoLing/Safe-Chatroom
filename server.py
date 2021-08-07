import asyncio
import websockets
import time
text=''
server_name='0号聊天室'


def loadaccounts():
    global adict,color
    i=0
    file= open('accounts.txt','r')
    for line in file.readlines():
        line = line.strip()
        k = line.split(' ')[0]
        v = line.split(' ')[1]
        adict[k] = v
        color[k] = line.split(' ')[2]
        i += 1
    file.close()
    print('Current accounts:')
    print(adict)
def loadadmins():
    global admins
    admins=[]
    file= open('admins.txt','r')
    for line in file.readlines():
        line = line.strip()
        admins.append(line)
    file.close()
    print('Current admins:')
    print(admins)
def admin(user):
    global admins
    if user not in admins:
        file= open('admins.txt','a')
        file.write('\n')
        file.write(user)
        file.close()
        loadadmins()
def deadmin(user):
    global admins
    if user in admins:
        admins.pop(admins.index(user))
        file= open('admins.txt','w')
        for i in range(len(admins)):
            file.write(admins[i])
            if i<len(admins)-1:
                file.write('\n')
        file.close()
        loadadmins()
adict = {}
color = {}
loadaccounts()
admins=[]
kicklist=[]
loadadmins()
async def main(websocket, path):
    global text,kicklist
    switcher = await websocket.recv()
    if switcher=='0':#登录
        username=await websocket.recv()
        password=await websocket.recv()
        if username in adict and adict[username] ==password:#用户名密码登录
            await websocket.send('Logged in.')
            await websocket.send(server_name)
            await websocket.send(text)
            await websocket.send(color[username])
            qq=await websocket.recv()
            file = open('log_qq.txt', 'a')
            file.write('['+str(time.strftime("%H:%M:%S", time.localtime()))+']'+username+' logged in with QQ:' + qq + '\n')
            file.close()
        if username not in adict and password=='':#游客登录并防止游客用已注册的用户ID登录
            #await websocket.send('Logged in.') #暂时禁用
            await websocket.send(server_name)
            await websocket.send(text)
        else:await websocket.send('Login failed.')
    if switcher=='1':#客户端发送消息
        username=await websocket.recv()
        textr=await websocket.recv()
        if textr[0]!=r'/':
            if username in adict:
                text = '['+str(time.strftime("%H:%M:%S", time.localtime()))+']'+username+':'+textr+'\n'+text
            else:text = '['+str(time.strftime("%H:%M:%S", time.localtime()))+']'+'[guest]'+username+':'+textr+'\n'+text
            await websocket.send('Message received.')
            await websocket.send(text)
        if textr[0]==r'/':
            global admins
            if username in admins:
                cmd=textr[1:].split(' ')#命令处理
                if cmd[0]=='loadaccounts':
                    loadaccounts()
                    await websocket.send('Command received.')
                if cmd[0]=='clear':
                    text=''
                    await websocket.send('Command received.')
                if cmd[0]=='admin':
                    if len(cmd)==2:
                        admin(cmd[1])
                        await websocket.send('Command received.')
                    else:
                        await websocket.send('Command error.')
                if cmd[0]=='kick':
                    if len(cmd)==2:
                        if cmd[1] not in kicklist:
                            kicklist.append(cmd[1])
                        await websocket.send('Command received.')
                    else:
                        await websocket.send('Command error.')
                if cmd[0]=='deadmin':
                    if len(cmd)==2:
                        deadmin(cmd[1])
                        await websocket.send('Command received.')
                    else:
                        await websocket.send('Command error.')
                if cmd[0]=='loadadmins':
                    loadadmins()
                    await websocket.send('Command received.')
                else:
                    await websocket.send('Command error.')
            else:await websocket.send('Command error.')

    if switcher=='2':#客户端发送刷新消息请求
        a=await websocket.recv()
        if a in kicklist:
            await websocket.send('Kicked out.')
            kicklist.pop(kicklist.index(a))
        else:await websocket.send(text)
start_server = websockets.serve(main, '0.0.0.0', 25565)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()