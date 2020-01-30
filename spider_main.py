#-*-coding:utf-8-*-
import urllib.request
from bs4 import BeautifulSoup
import time
import re
import pymysql
import tkinter
import threading


class SpiderMain(object):

    def __init__(self):
        self.max_experience ={'name':'','exp':0,'id':''}
        self.new_user_url=set()
        self.old_user_url=set()
        #self.lasttime=time.time()

    def add_user_url(self, url):
        if url is not None and url not in self.new_user_url and url not in self.old_user_url:
            self.new_user_url.add(url)

    def has_user_url(self):
        return len(self.new_user_url)!=0

    def get_user_url(self):
        old_url=self.new_user_url.pop()
        self.old_user_url.add(old_url)
        return old_url

    def download(self,url):
        # handler=urllib.request.ProxyHandler({'http':'171.39.40.110:8123','http':'121.232.146.106:9000','http':'121.232.146.150:9000'})
        # opener=urllib.request.build_opener(handler)
        # urllib.request.install_opener(opener)
        #if time.time()-self.lasttime<0.5:
        #    time.sleep(0.3)
        request=urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5;Windows NT)')
        response=urllib.request.urlopen(request)
        #self.lasttime=time.time()
        if response.status!=200:
            return
        return response.read()

    def parse(self, html_cont,id_url):
        exp_and_name={}
        if html_cont is None:
            return
        soup=BeautifulSoup(html_cont,'html.parser',from_encoding='utf-8')
        name=soup.find('h3',class_='user-name clearfix').find('span').get_text()
        exp=int(soup.find('span',class_='u-info-mp').find('em').get_text())
        sex=soup.find('span',class_='gender')['title']
        learntime=soup.find('span',class_='u-info-learn').find('em').get_text()
        points=soup.find('span',class_='u-info-credit').find('em').get_text()
        exp_and_name['name']=name
        exp_and_name['exp']=exp
        exp_and_name['id']=int(re.search(r'\d+',id_url).group())
        exp_and_name['sex']=sex
        exp_and_name['points']=points
        exp_and_name['learntime']=learntime
        return exp_and_name

#<h3 class="user-name clearfix"><span>weibo_fate自身难保_0</span>
#<span class="u-info-mp">经验<em>16295</em></span>

    def get_max_experience(self, exp_and_name):
        if exp_and_name['exp']>self.max_experience['exp']:
            self.max_experience['name']=exp_and_name['name']
            self.max_experience['exp']=exp_and_name['exp']
            self.max_experience['id']=exp_and_name['id']
            self.max_experience['sex']=exp_and_name['sex']
            self.max_experience['points']=exp_and_name['points']
            self.max_experience['learntime']=exp_and_name['learntime']

    def parse_user(self, follows_url):
        html_cont=self.download(follows_url)
        soup=BeautifulSoup(html_cont,'html.parser',from_encoding='utf-8')
        user_node=soup.find_all('div',class_='title')
        for one_node in user_node:
            user_url='http://www.imooc.com'+one_node.find('a')['href']
            if user_url!='http://www.imooc.com/u/10000' and user_url is not None:
                self.add_user_url(user_url)

    def store_user(self,id, name,sex,learntime,points, experience):
        try:
            db=pymysql.connect(host='localhost',user='root',passwd='12345678',db='db_database11',charset='utf8')
            cu=db.cursor()
            sql1='select * from tb_imooc1 where id=%d' %id
            cu.execute(sql1)
            if cu.fetchone() is None:
                sql='insert into tb_imooc1(id,name,sex,learntime,points,experience) values(%d,"%s","%s","%s","%s",%d)' %(id,name,sex,learntime,points,experience)
                cu.execute(sql)
                if cu.rowcount!=1:
                    raise Exception
                db.commit()
                cu.close()
                db.close()
                return True
        except Exception as e:
            print(e)
            db.rollback()
        cu.close()
        db.close()

    def continue_download(self):
        try:
            db=pymysql.connect(host='localhost',user='root',passwd='12345678',db='db_database11',charset='utf8')
            cu=db.cursor()
            sql='select * from tb_imooc1'
            cu.execute(sql)
            if len(cu.fetchall())==1000:
                return False
            return True
        except Exception as e:
            print(e)

#<div class="title"><a href="/u/106083" target="_blank">

if __name__=='__main__':
    def main():
        vart.set("开始爬取……")
        spider=SpiderMain()
        root_url='http://www.imooc.com/u/1979582'
        spider.add_user_url(root_url)
        while True:
            if start_stop_thread.is_stop==True:
                break
            try:
                if spider.has_user_url():
                    new_url=spider.get_user_url()
                    html_cont=spider.download(new_url)
                    exp_and_name=spider.parse(html_cont,new_url)
                    spider.parse_user(new_url+'/follows')
                    spider.get_max_experience(exp_and_name)
                    if spider.store_user(exp_and_name['id'],exp_and_name['name'],exp_and_name['sex'],exp_and_name['learntime'],exp_and_name['points'],exp_and_name['exp'])==True:
                        print(exp_and_name,end='    ')
                        print(spider.max_experience)
                        text_box.insert(tkinter.END,exp_and_name)
                        text_box.insert(tkinter.END,"\n")
                    else:
                        continue
                else:
                    break
            except:
                print('craw failure')
            if spider.continue_download()==False:
                print('download success')
                text_box.insert(tkinter.END,"download success\n")
                break
        print('the max experience is in http://www.imooc.com%s' %spider.max_experience['name'])
        print('the max experience is %d' %spider.max_experience['exp'])
        print("the max experience's id is %s" %spider.max_experience['id'])
        text_box.insert(tkinter.END,'the max experience is in http://www.imooc.com/u/%s    ' %spider.max_experience['id']+'the max experience is %d    ' %spider.max_experience['exp']+"the max experience's id is %s    " %spider.max_experience['name']+"\n")

    class start_stop_thread(object):
        is_stop=False
        def start_thread(self):
            start_stop_thread.is_stop=False
            text_box.delete(0.0,tkinter.END)
            text_box.insert(tkinter.END,"start threading\n")
            print('start threading')
            self.thr=threading.Thread(target=main)
            self.thr.start()

        def stop_thread(self):
            print('stop threading')
            text_box.insert(tkinter.END,"stop threading\n")
            start_stop_thread.is_stop=True
            vart.set('线程已停止...')

    #建立了一个新的窗口
    root=tkinter.Tk()
    root.wm_title('spider')#设置窗口左上角的文字
    root.wm_geometry('600x500+350+100')#设置窗口大小widthxheight+x+y
    root.iconbitmap('Spider_128px_1191381_easyicon.net.ico')#设置窗口图标

    def scrollcall(*args):
        scroll_bar.set(args[1],0)
    #
    scroll_bar=tkinter.Scrollbar(root,command=scrollcall)#设置滚动条
    scroll_bar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
    scroll_bar.set(0,0)
    #
    text_box=tkinter.Text(root)#设置文本框
    text_box.config(yscrollcommand=scroll_bar.set,height=36,background='#ffffff',font=('宋体',10),fg='#0000CD')
    text_box.pack()
    #
    # #将滚动条和text绑定起来
    # #text_box['yscrollcommand']=scroll_bar.set
    # #scroll_bar['command']=text_box.yview
    scroll_bar.config(command=text_box.yview)

    #scroll_text=ScrolledText(background='#cccccc',height=36)
    #scroll_text.pack()
    thread_new=start_stop_thread()

    button=tkinter.Button(root,text='确认爬取',font=('宋体',10),command=thread_new.start_thread)#设置按钮
    button.pack()

    button_stop=tkinter.Button(root,text='退出程序',font=('宋体',10),command=thread_new.stop_thread)
    button_stop.place(relx=0.7,rely=0.965,anchor=tkinter.CENTER)

    vart=tkinter.StringVar()
    vart.set('爬虫已准备，点击开始...')
    label=tkinter.Label(root,textvariable=vart,font=('宋体',10),fg='red')
    #label.place(x=28,y=475,anchor=tkinter.NW)
    label.place(relx=0.25,rely=0.97,anchor=tkinter.CENTER)
    root.mainloop()
    exit()
    #requests.get(url,headers=headers).text
    #threading.Thread(target=write).start()#开启一个线程
    #text.insert(END,string)


