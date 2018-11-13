from django.shortcuts import render
from.models import chat,dbname2,effectModel
import myapp.models
from django.http import HttpResponse

import time
from django.views.decorators.csrf import csrf_exempt

from test.similar import *

# effectModel.objects.create(time=time.strftime('%Y.%m.%d.%H.%M.%S',time.localtime(time.time())),valid=0,invalid=0,dialogue_count=0)
# Create your views here.
def hello_post(request):   #请求界面
    return render(request,"聊天框.html",)

def mongo(request):   #存数据库
    if request.GET:
        url = 'http://127.0.0.1:5000/'+request.GET['ques']
        ans0 = requests.get(url).text
        que1 = request.GET['ques']  # 获取用户提的问题
        count = list(chat.find())
        nona = list(dbname2.find())
        ques = Get_Qlist(count)
        noan_ques = Get_Qlist(nona)
        q = matching_question(ques, que1)
        no_q = matching_question(noan_ques,que1)
        ans = Get_Ans(count, q)  # 获取问答库的答案

        request.session.set_expiry(0)
        id = request.session.session_key

        l = effectModel.objects.all()
        length=len(l)-1

        count1 = l[length].dialog_count + 1
        count2 = count1 - l[length].invalid
        l[length].update(dialog_count=count1,valid = count2)

        if ans0 !='':
            return HttpResponse(ans0)
        elif ans0 =='' and ans == False:
            sv_q = Save_Ques(nona, no_q)  # 未回答问题
            return HttpResponse(sv_q)
        else:
            return HttpResponse(ans)


#获取全部数据
def find():
    result = chat.objects.filter()
    dict_data = {'data':result}
    return dict_data

def paisen(request):
    return render(request,"极客学院.html")

def denglu(request):
    return render(request,"new_file.html")

def user(request):
    #高频问题
    high_ques = []
    count = []
    all_count = myapp.models.chat.objects.all()
    for i in all_count:
        if i['count']>5:
            count.append(i['count'])
            high_ques.append(str(i['qs']))

    #未回答问题
    no_ques = []
    no_count = []
    FQ = myapp.models.dbname2.objects.all()
    for j in FQ:
        no_count.append(j['count'])
        no_ques.append(str(j['qs']))

    #回答问题数量和会话量
    dia_c = 0
    no_dia = 0
    session_c = 0
    no_session = 0
    dialog_count = myapp.models.effectModel.objects.all()
    for m in dialog_count:
        dia_c += m['dialog_count']
        no_dia += m['invalid']
        session_c+=1
        if m['dialog_count'] == 0:
            no_session+=1

    #趋势图
    s_count = [0,0,0,0,0,0,0]   #会话次数
    for n in dialog_count:
        time = int(n['time'][11:13])
        if time >= 0 and time < 4:
            s_count[1]+=1
        elif time < 8 :
            s_count[2] += 1
        elif time < 12 :
            s_count[3] += 1
        elif time < 16 :
            s_count[4] += 1
        elif time < 20 :
            s_count[5] += 1
        elif time <= 24:
            s_count[6] += 1

    return render(request,"user.html",{'count':count,'high_ques':high_ques,'no_ques':no_ques,'no_count':no_count,
                                       'dia_c':dia_c,'no_dia':no_dia,'va_dia':(dia_c-no_dia),
                                       'session':session_c,'nosession':no_session,'vasession':(session_c-no_session),
                                       's_count':s_count})

def date(request):
    alldate = {}
    if request.POST:
        if 'all' in request.POST.keys():
            alldate = myapp.models.chat.objects.all()
        if 'add' in request.POST.keys():
            if request.POST['question'].replace(' ', '') == '' or request.POST['answer'].replace(' ', '') == '':
                alldate =myapp.models.chat.objects.all()
            else:
                myapp.models.chat.objects.create(qs=request.POST['question'],an = request.POST['answer'], count=0)
                alldate = myapp.models.chat.objects.all()
        if 'del' in request.POST.keys():
            myapp.models.chat.objects.filter(qs=request.POST['question'].replace(' ', '')).delete()
            alldate = myapp.models.chat.objects.all()
        if 'update' in request.POST.keys():
            myapp.models.chat.objects.filter(qs=request.POST['question']).update(qs=request.POST['question'], an=request.POST['answer'])
            alldate = myapp.models.chat.objects.all()
        if 'find' in request.POST.keys():
            alldate = myapp.models.chat.objects.filter(qs=request.POST['question'])
        if 'noan' in request.POST.keys():
            alldate = myapp.models.dbname2.objects.all()

    return render(request, "date.html", {'alldate': alldate})
#按钮：有用没用
@csrf_exempt
def effect(request):
    if request.POST:
        l = effectModel.objects.all()
        length = len(l) - 1
        if request.POST['type'] == 'invalid':
            count1 = l[length].invalid + 1
            l[length].update(invalid=count1)
    else:
        l = effectModel.objects.all()
        length = len(l) - 1
        count2 = l[length].valid + 1
        l[length].update(valid=count2)
    return HttpResponse()
#超时刷新界面
@csrf_exempt
def timeout(request):
    if request.POST:
        if request.POST['timeout']=='add':
            nowtime = time.strftime('%Y.%m.%d.%H.%M.%S',time.localtime(time.time()))
            effectModel.objects.create(time=nowtime, valid=0, invalid=0, dialog_count=0)
        return HttpResponse()
# 点击图标进入机器人聊天界面
@csrf_exempt
def goin(request):
    request.session.set_expiry(15*60)
    id = request.session.session_key
    if request.POST:
        if request.POST['goin']=='add':
            nowtime = time.strftime('%Y.%m.%d.%H.%M.%S',time.localtime(time.time()))
            effectModel.objects.create(se_id=id,time=nowtime,valid=0,invalid=0,dialog_count=0)
            l = effectModel.objects.all()
            length = len(l) - 1
            print(l,length,l[length])
        return HttpResponse()