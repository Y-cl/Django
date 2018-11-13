
import jieba
import numpy as np
import difflib
import requests

from pymongo import MongoClient


conn = MongoClient('127.0.0.1',27017)
db = conn.chatroom
chat = db.chat
dbname2 = db.dbname2
# count = list(QA.find())





def Get_Qlist(lst):
    ques = []
    for i in lst:
        ques.append(i['qs'])
    return ques






#创建停用词list
def stopwordlist(filepath):
    stopwords = [line.strip() for line in open(filepath,'r',encoding='utf-8').readlines()]
    return stopwords[0]

# 调用停用词，对语句进行分词处理，为计算相似度做准备
def seg_sentence(sentence):
    question = {}
    sentence_seged = jieba.cut(sentence.strip())
    stopwords = stopwordlist(r'D:/stopword.txt')
    outstr = ''
    for word in sentence_seged:
        if word not in stopwords:
            if word != '\t':
                outstr += word
                outstr += ''
    question[outstr] = sentence
    return question



#计算用户问题和问答库中问题的相似度
def cal_similiar(question,sen):
    str_data = {}
    length = len(sen)
    median_list = {}
    for item in question.keys():         #调节因字符串长短而导致的相似度误差问题
        num = np.median([len(item),length])
        if abs(length - num) != 0:
            xx = (abs(length - num)) * 0.009   #自定义一个权值
        else:
            xx = 0
        median_list[item] = xx     #xx为偏移量

    for k,v in median_list.items():     #重新计算语句相似度，并返回字典形式为问答库内问题及该问题与用户问题的相似度
        fraction = difflib.SequenceMatcher(None,sen,k).quick_ratio()-v
        s = question[k]
        str_data[s] = fraction    #语句相似度

    return str_data


#根据计算后的相似度进行问答库内问题匹配
def matching_question(lst,sen):
    px = {}
    for i in lst:
        question = seg_sentence(i)       #调用停用词处理函数，返回字典
        str_data = cal_similiar(question,sen)       #调用计算相似度算法，参数为停用词函数返回的字典
        for k,v in str_data.items():
            px[i] = v
    tupl_data = sorted(px.items(),key=lambda x:x[1], reverse=True)
    for item in tupl_data:
        if item[1] > 0.3:

            return tupl_data[0][0]
        else:
            return sen

# qustion = matching_question(ques,que1)
def Get_Ans(qu,qustion):
    for i in qu:

        if i['qs'] == qustion:
            i['count'] += 1
            chat.update({'qs': qustion}, {'$set': {'count': i['count']}})
            return i['an']
    else:
        return False
def Save_Ques(no_q,no_qustion):
        if no_qustion not in  Get_Qlist(no_q):
            dbname2.insert({'qs':no_qustion,'an':'', 'count': 1})
        else:
            for i in no_q:
                if i['qs'] == no_qustion:
                    i['count'] += 1
                    dbname2.update({'qs': no_qustion}, {'$set': {'count': i['count']}})
        return '这个问题太难了，我还没有学习到哦，我会继续努力学习的亲，么么哒~~！'









