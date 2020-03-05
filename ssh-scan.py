import socket
import sys
import threading
import signal

portMutex=threading.Lock()
openMutex=threading.Lock()
port=1
openPorts=[]


def sigint(signum, frame):
   global portMutex
   global port

   portMutex.acquire()
   port=65536
   portMutex.release()

def ssh_checker_worker(ip):
   global portMutex
   global openMutex
   global jobMutex
   global port
   global openPorts

   while True:
      portMutex.acquire()
      myPort=port
      port+=1
      portMutex.release()
      if myPort > 65535:
         return

      try:
         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      except Exception:
         return

      sock.settimeout(2)
      try:
         sock.connect((ip, myPort))
         data=sock.recv(1024)
         if "OpenSSH" in data:
            openMutex.acquire()
            print "ssh port %s is open" % myPort
            openPorts+=[myPort]
            openMutex.release()
      except Exception:
         pass
      finally:
         sock.close()

def main():
   threadPool=[]

   if len(sys.argv) != 2:
      print "Issue the command like this: \n\tpython %s YOUR-TARGET-IP" % sys.argv[0]
      return 1

   ip=sys.argv[1]
   signal.signal(signal.SIGINT, sigint)
   for _ in range(1000):
      thread=threading.Thread(target=ssh_checker_worker, args=(ip,))
      thread.start()
      threadPool+=[thread]
   
   for worker in threadPool:
      while worker.isAlive():
         worker.join(timeout=1)

   openPorts.sort()
   print "list of open ssh ports exposed to the public Internet:"
   print "============================================================"
   for openPort in openPorts:
      print "TCP/%s" % openPort

if __name__=="__main__":
   sys.exit(main())
