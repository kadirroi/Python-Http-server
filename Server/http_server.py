# -*- coding: utf-8 -*-
import socket
from multiprocessing import Process,current_process,Queue
import sys,time


def log (Qlog):
    print(current_process().name)
    while True:
        if Qlog.qsize()>0:
          
            queueData=Qlog.get()
            if queueData[0]=="ACCESS":
               
                t = time.ctime()
                fa=open("accept.log","a")
                fa.write(t+": "+queueData[1]+" "+queueData[2]+" "+queueData[3]+"\n")
                fa.close()
            else:
                t = time.ctime()
                fb=open("error.log","a")
                fb.write(t+": "+queueData[1]+" "+queueData[2]+" "+queueData[3]+"\n")
                fb.close()
                
                





def test(name,cSocket,cAddr,Qlog,Qcount):
    
    cSocket.settimeout(60)
    print(current_process().name)
    try:
        data=cSocket.recv(1024)
        if data[0:3]=="GET":
            if len(data)<14:
                cSocket.send('HTTP/1.0 400 \n')
                msq=("ERROR","GET","istek yapısı bozuk","HTTP/1.0 400 ") 
                Qlog.put(msq)
                Qcount.get()
                cSocket.close() 
                
            elif data[3]==" "and data[4]=="/" and data[5]==" " and data.index("HTTP/1.1")==6:
            
                cSocket.send('HTTP/1.0 200 OK\n')
                cSocket.send('Content-Type: text/html\n')
                cSocket.send('\n') 
                cSocket.send("""<html>\n<body>\n<ul>\n<li>Page1.html</li>\n<li>Page2.html</li>\n<li>Page3.html</li>\n</ul>\n</body>\n</html>
                     """)
                msq=("ACCESS","GET","/","HTTP/1.0 200 OK") 
                Qlog.put(msq)
                Qcount.get()
                cSocket.close() 
                 
          
            elif data[3]==" " and data[4]=="/" and "html" in data[data.index("/")+1:data.index("HTTP/1.1")-1]:
                if data[data.index("/")+1:data.index("HTTP/1.1")-1] in pages:
                    f=open(data[data.index("/")+1:data.index("HTTP/1.1")-1],'r')
                    cSocket.send('HTTP/1.0 200 OK\n')
                    cSocket.send('Content-Type: text/html\n')
                    cSocket.send('\n') 
                    cSocket.send(f.read())
                    msq=("ACCESS","GET",data[data.index("/")+1:data.index("HTTP/1.1")-1],"HTTP/1.0 200 OK")
                    Qlog.put(msq)
                    Qcount.get()
                    cSocket.close() 
                
                else:
                    cSocket.send('HTTP/1.0 404 \n')
                    msq=("ERROR","GET",data[data.index("/")+1:data.index("HTTP/1.1")-1],"HTTP/1.0 404 Page not found")
                    Qlog.put(msq)
                    Qcount.get()
                    cSocket.close() 
                


        elif data[0:4]=="HEAD":
            if len(data)<15:
                cSocket.send('HTTP/1.0 400 \n')
                msq=("ERROR","HEAD","istek yapısı bozuk","HTTP/1.0 400 ") 
                Qlog.put(msq)
                Qcount.get() 
                cSocket.close() 

            elif data[4]==" " and data[5]=="/" and data[6]==" " and data.index("HTTP/1.1")==7:
                cSocket.send('HTTP/1.0 200 OK\n')
                cSocket.send('Content-Type: text/html\n')
                cSocket.send('Server Kadir\n')
                cSocket.send('Date '+time.ctime())
                cSocket.send('Lenght: 350\n')
                msq=("ACCESS","HEAD","/","HTTP/1.0 200 OK") 
                Qlog.put(msq)
                Qcount.get() 
                cSocket.close() 
            elif data[4]==" " and data[5]=="/" and "html" in data[data.index("/")+1:data.index("HTTP/1.1")-1]:
                if data[data.index("/")+1:data.index("HTTP/1.1")-1] in pages:
                    f=open(data[data.index("/")+1:data.index("HTTP/1.1")-1],'r')
                    cSocket.send('HTTP/1.0 200 OK\n')
                    cSocket.send('Content-Type: text/html\n')
                    cSocket.send('Server Kadir\n')
                    cSocket.send('Date '+time.ctime()+'\n')
                    cSocket.send("Lenght: "+str(len(f.read())))
                    msq=("ACCESS","HEAD","/"+data[data.index("/")+1:data.index("HTTP/1.1")-1],"HTTP/1.0 200 OK") 
                    Qlog.put(msq)
                    Qcount.get() 
                    cSocket.close() 
                else:
                    cSocket.send('HTTP/1.0 404 Page not found\n')
                    cSocket.send('Content-Type: text/html\n')
                    cSocket.send('Server Kadir\n')
                    cSocket.send('Date '+time.ctime())
                    msq=("ERROR","HEAD",data[data.index("/")+1:data.index("HTTP/1.1")-1],"HTTP/1.0 404 Page not found")
                    Qlog.put(msq)
                    Qcount.get() 
                    cSocket.close()             
                     
                                 
                    
                    
            else:
                cSocket.send('HTTP/1.0 400 \n')
                msq=("ERROR","HEAD","istek yapısı bozuk","HTTP/1.0 400 ")
                Qlog.put(msq)
                Qcount.get() 
                cSocket.close()
            


        else:
             cSocket.send('HTTP/1.0 501 \n')
             msq=("ERROR",data[0:4],"istek metodu tanınmıyor","HTTP/1.0 501") 
             Qlog.put(msq)
             Qcount.get() 
             cSocket.close()

    except socket.timeout, e:
        err = e.args[0]
        if err == 'timed out':
            cSocket.send('HTTP/1.0 408 \n')
            msq=("ERROR","Time Out","istek yapılmadı","HTTP/1.0 408") 
            Qlog.put(msq)
            Qcount.get() 
            cSocket.close()
           
            
            
Qlog=Queue()
Qcount=Queue()
pages=["page1.html","page2.html","page3.html"]
a=Process(target=log, args=(Qlog,))
a.start()
s=socket.socket()
host="127.0.0.1"
port=12345
s.bind((host,port))

s.listen(3)
count=0
while True:
    c,addr=s.accept()
   
    
    print 'Got connection from',addr
    print(Qcount.qsize())
    if Qcount.qsize()<4:
        Qcount.put("True")
	p = Process(target=test, args=("Process",c,addr,Qlog,Qcount))
    	p.start()
    else:
        c.send('HTTP/1.0 503 \n')
        msq=("ERROR"," ","Daha fazla Proces yaratılamaz","HTTP/1.0 503 ")
        Qlog.put(msq)
        c.close()
    

   
   
