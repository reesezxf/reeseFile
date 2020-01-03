# -*-encoding:utf-8 -*-

import collections
import datetime
import json
import os
import sys
import uuid
import math
# import redis
from dateutil.relativedelta import relativedelta
from django.db.models import Sum,F,FloatField
from datetime import timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt

from NPI_EERF.models import *
from django.db.models import Q

reload(sys)
sys.setdefaultencoding('utf-8')
ZHONGGAN = [u'中干', u'中幹']
MANAGEMENT_LIST = [u'專理', u'資深專理', u'副理', u'資深副理', u'經理', u'資深經理', u'處長']
UPDATE_DATA_DATE = 5  # 更新数据的日期 每个月5号

def tip(request):
    """
    使用IE浏览器跳转提示页面。
    :param request:
    :return:
    """
    return render_to_response('NPI_EERF/tip.html')
def get_leader():
    """
    :Author: F1233225
    :Date: 2019-01-09
    根据部门编号获取 每个部门的leader
    :return:
    """
    leader_list = []
    leader_list_id = []
    for leader in ELeader.objects.all().order_by('edepartment_num'):
        leader_data = EEmployee.objects.get(
            e_id__exact=EDepartment.objects.get(d_id__exact=leader.edepartment_id).d_leadernum).e_ename
        if leader_data not in leader_list:
            leader_list.append(leader_data)
    return leader_list

def get_section():
    """
    :Author: F1237077
    :Date: 2019-07-17
    根据部门编号获取 每个科级的英文名
    :return:
    """
    leader_list = []
    for leader in ESubjectTeam.objects.all().order_by('st_team'):
        leader_data =leader.st_team
        if leader_data not in leader_list:
            leader_list.append(leader_data)
    return leader_list

def split_para(para):
    """
    :Author: F1233225
    :Date: 2019-01-09
    处理前台传进来的参数
    :param para:
    :return:list
    """
    list = []
    para = para.split('_')
    for i in para:
        if i:
            list.append(i)
    return list


def get_all_team_data():
    """
    :Author: F1233225
    :Date: 2019-01-09
    获取所有team的常设、浪花数据，用在招募状况页面
    :return:all_team_data
    """
    all_team_data = []
    leader_list = get_leader()
    for _leader in leader_list:
        for j, h in enumerate(EHumans.objects.all()):
            if _leader == h.h_ename:
                eachteam_data = {}
                eachteam_data['name'] = h.h_team
                eachteam_data['num'] = h.h_taiwan + h.h_mesome + h.h_technician + h.h_spindrift
                eachteam_data['always'] = h.h_taiwan + h.h_mesome + h.h_technician
                eachteam_data['spindrift'] = h.h_spindrift
                if eachteam_data not in all_team_data:
                    all_team_data.append(eachteam_data)
    # all_team_data.sort(key=lambda x:-x['num']) # 对 num 倒序排序
    return all_team_data


def replace_val(old_val):
    """
    @note: 去掉特殊符号 [' ', '#', '!', '$', '%', '^', '&', '*', '~']
    """
    old_val = old_val.replace(" ", "")
    old_val = old_val.replace("&", "")
    old_val = old_val.replace("/", "")
    old_val = old_val.replace("$", "")
    return old_val


def get_CnameAndAuthority(username):
    """
    :Author: F1233225
    :Date: 2019-01-09
    根据用户名 获取中文名及职级
    :param username:
    :return:用户的中文名，职级
    """
    user = EEmployee.objects.get(e_id__exact=username)
    user_cname = user.e_cname
    user_authority = user.e_management
    return user_cname, user_authority


@csrf_exempt
def index(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    index界面：
    :param req:
    :return:用户中文名、职级、权限
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        user = EEmployee.objects.get(e_id__exact=username)
        user_cname = user.e_cname
        user_authority = user.e_management
        user_chmod = user.e_chmod
        response = render_to_response('NPI_EERF/index.html',
                                      {'user_cname': user_cname, 'user_authority': user_authority,
                                       'user_chmod': user_chmod}, context_instance=RequestContext(req))
        #         response.set_cookie('eerf_user',username,3600)
        return response
    else:
        return HttpResponseRedirect('/login/')


@csrf_exempt
def login(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    登陆
    :param req:
    :return: 判断用户登陆结果，给出提示
    """
    if req.method == 'POST':
        username = req.POST['username']
        pwd = req.POST['password']
        empl_user = EEmployee.objects.filter(e_id__exact=username)
        empl_pwd = EEmployee.objects.filter(e_id__exact=username, e_pwd__exact=pwd)
        # print(empl_pwd[0].e_cname)
        if empl_user:
            if empl_pwd:
                if empl_pwd.filter(e_chmod='admin') or empl_pwd.filter(e_management__in=MANAGEMENT_LIST):
                    response = HttpResponseRedirect('/index/')
                    response.set_cookie('eerf_user', username, 1800)
                    return response
                else:
                    # ?以下代码有雷同，可否优化
                    return render_to_response('NPI_EERF/login.html', {'authority': False},
                                              context_instance=RequestContext(req))
            else:
                return render_to_response('NPI_EERF/login.html', {'pwd_is_wrong': True},
                                          context_instance=RequestContext(req))
        else:
            return render_to_response('NPI_EERF/login.html', {'user_is_wrong': True},
                                      context_instance=RequestContext(req))

    return render_to_response('NPI_EERF/login.html', context_instance=RequestContext(req))


@csrf_exempt
def change_pwd(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    登陆页面 修改密码
    :param req:
    :return:修改结果
    """
    if req.method == 'POST':
        change_user = req.POST.get('update_user')
        old_pwd = req.POST.get('old_pwd')
        new_pwd = req.POST.get('new_pwd')
        # print change_user, old_pwd, new_pwd
        if EEmployee.objects.filter(e_id__exact=change_user):
            if EEmployee.objects.filter(e_id__exact=change_user, e_pwd__exact=old_pwd):
                the_user = EEmployee.objects.get(e_id__exact=change_user)
                the_user.e_pwd = new_pwd
                the_user.save()
                change_status = 'success'
            else:
                change_status = 'old_pwd'
        else:
            change_status = 'user'
        return HttpResponse(json.dumps(change_status))


def logout(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    登出，删掉cookie
    :param req:
    :return:login界面
    """
    response = HttpResponseRedirect('/login/')
    response.delete_cookie('eerf_user')
    return response


def getGradeList():
    """
    :Author: F1233225
    :Date: 2019-01-09
    获得EERF所有在职、常设人员的资位，并排序 从员1--师13
    :return:
    """
    # category_list = [u'借調', u'支援']
    grade_list = []
    all_grade = list(
        EEmployee.objects.filter(e_status__exact=u'在職', e_category__exact=u'常設').values_list('e_grade', flat=True))
    for i, grade in enumerate(all_grade):
        if '預' not in grade:
            if '試用' not in grade:
                if grade != u'無' and grade not in grade_list:
                    grade_list.append(grade)
    grade_list = sorted(grade_list)
    # print(json.dumps(grade_list,ensure_ascii=False))
    grade_list.sort(key=sort_yuanji)
    grade_list.sort(key=sort_shiji)

    return grade_list


def sort_shiji(level):
    """
    :Author: F1233225
    :Date: 2019-01-09
    对 师级资位 排序 师1--13
    :param level:
    :return:
    """
    if '師' in level:
        return int(level[level.index('師') + 1:])


def sort_yuanji(level):
    """
    :Author: F1233225
    :Date: 2019-01-09
    对 员级资位 排序 员1--3
    :param level:
    :return:
    """
    if '員' in level:
        return int(level[-1])


def power(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    获得power页面所需的数据， 每个leader（部）每个team的在职的台干、中干、员级、浪花的人数
    :param req:
    :return:每个leader（部）每个team的台干、中干、员级、浪花的人数
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        user_cname, user_authority = get_CnameAndAuthority(username)
        grade_list = getGradeList()

        # 获取人力实时状况
        ehumans = EHumans.objects.all().order_by('h_group')
        humans_list = []
        # 所有主管工号
        all_h_num = []
        leader_data = get_leader()
        for leader in leader_data:
            all_h_num.append(EEmployee.objects.get(e_ename__exact=leader).e_id)
        # 获取实时人力状况的数据,并添加进humans_list
        for every_num in all_h_num:
            every_humans = ehumans.filter(h_num__exact=every_num)
            each_human = {}
            each_human['h_ename'] = every_humans[0].h_ename
            each_human['h_taiwan'] = 0
            each_human['h_mesome'] = 0
            each_human['h_technician'] = 0
            each_human['h_spindrift'] = 0
            each_human['h_team_data'] = []
            for every_human in every_humans:
                each_team_data = {}
                each_team_data['name'] = every_human.h_team
                each_team_data['mesome'] = every_human.h_mesome
                each_team_data['taiwan'] = every_human.h_taiwan
                each_team_data['technician'] = every_human.h_technician
                each_team_data['spindrift'] = every_human.h_spindrift
                each_team_data['total'] = every_human.h_mesome + every_human.h_taiwan + \
                                          every_human.h_technician + every_human.h_spindrift

                each_human['h_team_data'].append(each_team_data)

                each_human['h_taiwan'] += every_human.h_taiwan
                each_human['h_mesome'] += every_human.h_mesome
                each_human['h_technician'] += every_human.h_technician
                each_human['h_spindrift'] += every_human.h_spindrift

            humans_list.append(each_human)

        response = render_to_response('NPI_EERF/Power.html',
                                      {'username': username, 'user_cname': user_cname, 'user_authority': user_authority,
                                       'humans_list': json.dumps(humans_list), 'grade_list': json.dumps(grade_list)})

        return response
    else:
        return HttpResponseRedirect('/login/')


@csrf_exempt
def power_ajax(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    根据用户选择的时间、资位筛选计算每个leader（部）每个team的台干、中干、员级、浪花的人数
    :param req:
    :return:
    """
    if req.POST:
        print('get ajax request')
        # 根据时间,资位进行人力筛选
        limit_time = req.POST.get('selectedTime')
        ziwei_list = req.POST.get('selectedGrade').split('_')
        # 获取前台传的时间，默认当天时间
        if limit_time:
            lastdate = datetime.datetime.strptime(limit_time, "%Y-%m-%d").date()
        else:
            lastdate = datetime.datetime.now().date()
        # print(type(lastdate), lastdate)
        # 资位列表
        grade_list = []
        for grade in ziwei_list:
            if grade != '':
                grade_list.append(u'試用' + grade)
                grade_list.append(u'預' + grade)
                grade_list.append(grade)
        # 所有leader数据
        all_leader_data = []
        print('before total:', EEmployee.objects.filter(e_grade__in=grade_list).count())
        # 常设 人力
        permanents = EEmployee.objects.filter(e_grade__in=grade_list, e_category__exact=u'常設', e_status__exact=u'在職')
        # 搜索时间 时候还没离职的常设人力
        permanents_before = EEmployee.objects.filter(e_grade__in=grade_list, e_category__exact=u'常設',
                                                     e_status__exact=u'離職', e_lastdate__gt=lastdate)
        category_list = [u'借調', u'支援']
        # 计算 浪花人数
        if lastdate >= datetime.date(2018, 3, 15):
            spindrift_empl = EEmployee.objects.filter(e_grade__in=grade_list, e_category__in=category_list,
                                                      e_status__exact=u'在職', e_expiringdate__gt=lastdate)
        else:
            spindrift_empl = EEmployee.objects.filter(e_grade__in=grade_list, e_category__in=category_list,
                                                      create_time__lte=datetime.date(2018, 3, 16),
                                                      e_status__exact=u'在職').exclude(e_expiringdate__lt=lastdate)

        # 获取each_leader_team
        leader_data = get_leader()
        all_leader_team = []
        for leader in leader_data:
            for ehuman in EHumans.objects.all().order_by('h_group'):
                if ehuman.h_ename == leader:
                    each_leader_team = {}
                    each_leader_team['leader_name'] = ehuman.h_ename
                    each_leader_team['team'] = []
                    for eh in EHumans.objects.filter(h_ename__exact=ehuman.h_ename):
                        each_leader_team['team'].append(eh.h_team)
            all_leader_team.append(each_leader_team)
        # Magma算单独一个leader(部)
        all_leader_team.append({'leader_name': u'Magma', 'team': [u'Magma']})
        # 获取all_leader数据
        for leader_team in all_leader_team:
            # each_leader数据初始化
            each_leader_data = {}
            each_leader_data['team_leader'] = leader_team['leader_name']
            each_leader_data['total'] = 0
            each_leader_data['taiwan'] = 0
            each_leader_data['mesome'] = 0
            each_leader_data['technician'] = 0
            each_leader_data['spindrift'] = 0
            each_leader_data['team_data'] = []
            # 获取each_leader_data数据
            for team in leader_team['team']:
                each_team_data = {}
                each_team_data['name'] = team
                each_team_data['total'] = permanents.filter(e_functionteam__exact=team).count() \
                                          + permanents_before.filter(e_functionteam__exact=team).count()
                each_team_data['taiwan'] = permanents.filter(e_functionteam__exact=team,
                                                             e_difference__exact=u'臺幹').count() \
                                           + permanents_before.filter(e_functionteam__exact=team,
                                                                      e_difference__exact=u'臺幹').count()
                each_team_data['technician'] = permanents.filter(e_functionteam__exact=team, e_difference__in=ZHONGGAN,
                                                                 e_grade__contains=u'員').count() \
                                               + permanents_before.filter(e_functionteam__exact=team,
                                                                          e_difference__in=ZHONGGAN,
                                                                          e_grade__contains=u'員').count()
                each_team_data['spindrift'] = spindrift_empl.filter(e_functionteam__exact=team).count()
                each_team_data['mesome'] = permanents.filter(e_functionteam__exact=team,
                                                             e_difference__in=ZHONGGAN).exclude(
                    e_grade__contains=u'員').count() \
                                           + permanents_before.filter(e_functionteam__exact=team,
                                                                      e_difference__in=ZHONGGAN).exclude(
                    e_grade__contains=u'員').count()
                each_leader_data['total'] += each_team_data['total']
                each_leader_data['taiwan'] += each_team_data['taiwan']
                each_leader_data['mesome'] += each_team_data['mesome']
                each_leader_data['technician'] += each_team_data['technician']
                each_leader_data['spindrift'] += each_team_data['spindrift']

                each_leader_data['team_data'].append(each_team_data)
            all_leader_data.append(each_leader_data)

        return HttpResponse(json.dumps(all_leader_data))


@csrf_exempt
def unitspower(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    获得 unitspower页面的 每个阶段 每个leader（部）的人力数据
    :param req:
    :return:
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        user_cname, user_authority = get_CnameAndAuthority(username)
        user_chmod = EEmployee.objects.get(e_id__exact=username).e_chmod
        team_id_list = []
        team_name_list = []
        pleader_list = []
        team_list = []
        leader_list = get_leader()

        for i, prov in enumerate(EProvide.objects.all()):
            if prov.p_leader not in pleader_list:
                pleader_list.append(prov.p_leader)
            if prov.eteam_id not in team_id_list:
                team_id_list.append(prov.eteam_id)

                # 获取each_team中的数据
                each_team = {}
                each_team['team_name'] = ETeam.objects.get(t_id__exact=prov.eteam_id).t_team
                team_name_list.append(each_team['team_name'])
                each_team['team_leader'] = EEmployee.objects.get(e_id__exact=EDepartment.objects
                                                                 .get(d_id__exact=ELeader.objects
                                                                      .get(l_id__exact=ETeam.objects
                                                                           .get(
                    t_id__exact=prov.eteam_id).eleader_id).edepartment_id).d_leadernum).e_ename

                each_team['p_data'] = []
                # 获取team_list
                for provide in EProvide.objects.filter(eteam_id__exact=prov.eteam_id):
                    temp_dic = {}
                    temp_dic['team_name'] = each_team['team_name']
                    temp_dic['team_leader'] = each_team['team_leader']
                    temp_dic['pleader'] = provide.p_leader
                    temp_dic['engineers'] = provide.p_engineers
                    team_list.append(temp_dic)

        # 数据 按照 每个阶段--每个leader 这样组织
        all_num = []
        # 获取each_pleader
        for pleader in pleader_list:
            each_pleader = {}
            each_pleader['pleader'] = pleader
            each_pleader['num_data'] = []
            # 获取each_team_data
            for leader_name in leader_list:
                each_team_data = {}
                each_team_data['leader_name'] = leader_name
                each_team_data['num'] = 0
                each_team_data['team_data'] = []
                # 获取each_team_data
                for team in team_list:
                    for team_name in team_name_list:
                        if team['pleader'] == pleader and team['team_leader'] == leader_name and team[
                            'team_name'] == team_name:
                            temp_dic = {}
                            temp_dic['team_name'] = team['team_name']
                            temp_dic['team_num'] = team['engineers']
                            each_team_data['num'] += team['engineers']
                            if temp_dic not in each_team_data['team_data']:
                                each_team_data['team_data'].append(temp_dic)
                each_pleader['num_data'].append(each_team_data)
            all_num.append(each_pleader)

        response = render_to_response('NPI_EERF/UnitsPower.html',
                                      {'username': username, 'user_cname': user_cname,
                                       'user_authority': user_authority, 'user_chmod': json.dumps(user_chmod),
                                       'pleader_list': pleader_list, 'all_ep_data': json.dumps(all_num)})
        return response
    else:
        return HttpResponseRedirect('/login/')


@csrf_exempt
def units_setting_ajax(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    unitspower页面的表格数据的加载 每个group 每个leader 每个team 在每个阶段的人力
    :param req:
    :return:response
    """
    if req.POST.get('info') == 'loaddata':

        sorted_leader = get_leader()  # 獲取leader數據
        provide_data = []  # provide数据列表
        group_list = []  # 组级列表
        team_leader_list = []  # team_leader列表
        team_list = []  # team列表
        # 获取each_provide
        for index, provide in enumerate(EProvide.objects.all()):
            each_provide = {}
            # 获取组级列表
            each_provide['group_name'] = ELeader.objects.get(
                l_id__exact=ETeam.objects.get(t_id__exact=provide.eteam_id).eleader_id).l_group
            if each_provide['group_name'] not in group_list:
                group_list.append(each_provide['group_name'])
            # 获取team_leader列表
            each_provide['leader_name'] = EEmployee.objects.get(e_id__exact=EDepartment.objects.get(
                d_id__exact=ELeader.objects.get(l_id__exact=ETeam.objects.get(
                    t_id__exact=provide.eteam_id).eleader_id).edepartment_id).d_leadernum).e_ename
            if each_provide['leader_name'] not in team_leader_list:
                team_leader_list.append(each_provide['leader_name'])
            # 获取provide数据
            each_provide['team_name'] = ETeam.objects.get(t_id__exact=provide.eteam_id).t_team
            each_provide['team_id'] = provide.eteam_id
            if each_provide['team_name'] not in team_list:
                team_list.append(each_provide['team_name'])
            each_provide['p_leader'] = provide.p_leader
            each_provide['engineers'] = provide.p_engineers
            provide_data.append(each_provide)

        # 1.sorted by team
        all_team_data = []
        # 获取all_team数据
        for team in team_list:
            each_team_data = {}
            each_team_data['team_name'] = team
            each_team_data['engineer_num'] = []
            # 获取each_team数据
            for group in group_list:
                for team_leader in team_leader_list:
                    for p_data in provide_data:
                        if p_data['group_name'] == group and p_data['leader_name'] == team_leader and p_data[
                            'team_name'] == team:
                            each_team_data['engineer_num'].append(p_data['engineers'])
                            each_team_data['group'] = group
                            each_team_data['team_leader'] = team_leader
                            each_team_data['leader_id'] = sorted_leader.index(team_leader)
                            each_team_data['team_id'] = p_data['team_id']
            all_team_data.append(each_team_data)
    # 排序
    all_team_data.sort(key=lambda x: [str(x['group']), x['leader_id']])
    return HttpResponse(json.dumps(all_team_data))


@csrf_exempt
def units_ajax(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    unitspower页面 表格数据的增删改， 根据前台传过来的参数sendMessage判断是什么操作
    :param req:
    :return:
    """
    if req.method == "POST":

        if req.POST.get('sendMessage') == 'update':
            # 获取each_list
            data = split_para(req.POST.get('data'))
            data_list = data[:len(data) - 1]
            for each in data_list:
                each_list = each.split(',')
                each_list = each_list[:len(each_list) - 1]
                # 获取teamId
                for i in range(1, len(each_list)):
                    if each_list[0].split('"')[0] == '':
                        team_id = each_list[0].split('"')[1]
                    else:
                        team_id = each_list[0]
                    # 获取ep_obj 并将其存储
                    prov_data = EProvide.objects.get(eteam_id__exact=team_id,
                                                     p_leader__exact=str(each_list[i].split(':')[0]))
                    if prov_data:
                        # print 'before update', ep_obj.p_engineers,ep_obj.p_leader,ep_obj.eteam_id
                        prov_data.p_engineers = int(each_list[i].split(':')[1])
                        # print 'after update',ep_obj.p_engineers
                        prov_data.save()

            message = 'update success'

            return HttpResponse(json.dumps(message))

        if req.POST.get('sendMessage') == 'add':
            all_add_val = split_para(req.POST.get('all_add_val'))
            all_id = split_para(req.POST.get('all_id'))
            for i, id in enumerate(all_id):
                team_data = ETeam.objects.get(t_id__exact=id)
                EProvide.objects.create(eteam=team_data, p_engineers=all_add_val[i + 1], p_technician=0,
                                        p_leader=all_add_val[0])

            message = 'add success'
            return HttpResponse(json.dumps(message))

        if req.POST.get('sendMessage') == 'delete':
            selected_pleader = split_para(req.POST.get('selected_pleader'))
            for leader in selected_pleader:
                EProvide.objects.filter(p_leader=leader).delete()
            return HttpResponse(json.dumps('delete success'))


@csrf_exempt
def historypower(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    历史趋势页面：只是展示每个月的总人力和固定人力
    :param req:
    :return:所有年份的数据
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        user_cname, user_authority = get_CnameAndAuthority(username)
        totalmans_data = ETotalmans.objects.all()
        # 筛选每一年第12(最大月份 不一定12)月份的t_always 和 t_headcount 然后 每一年每一月的 t_always 和 t_headcount
        all_years = []
        for i, total in enumerate(totalmans_data):
            if total.t_datetime.year not in all_years:
                all_years.append(total.t_datetime.year)
        all_years.sort()
        # 获取所有年份的数据
        all_years_data = []
        # 获取每年数据
        for year in all_years:
            every_year_data = []
            every_year = ETotalmans.objects.filter(t_datetime__year=year).order_by('t_datetime')
            for index, every_month in enumerate(every_year):
                every_month_data = {}
                every_month_data['year'] = every_month.t_datetime.year
                every_month_data['month'] = every_month.t_datetime.month
                every_month_data['fixed'] = every_month.t_engineers + every_month.t_technician
                every_month_data['total'] = every_month.t_engineers + every_month.t_technician \
                                            + every_month.t_supporter + every_month.t_loan
                every_year_data.append(every_month_data)
            all_years_data.append(every_year_data)
        response = render_to_response('NPI_EERF/HistoryPower.html',
                                      {'username': username, 'user_cname': user_cname, 'user_authority': user_authority,
                                       'all_years_data': json.dumps(all_years_data)})
        return response
    else:
        return HttpResponseRedirect('/login/')


def recruit(req):
    """
    招募状况
    :param req:
    :return:
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        user_cname, user_authority = get_CnameAndAuthority(username)
        edemand_data = EDemand.objects.filter(Q(d_application__year=datetime.date.today().year, d_status__in=['進行中','完成']) | Q(d_application__year=datetime.date.today().year-1, d_status__in=['進行中']))
        all_team_data = get_all_team_data()

        # 课---functionTeam 数据
        leader_data = get_leader()
        subject_functionTeam_dic = {}
        esubject_data = ESubjectTeam.objects.all()
        for es in esubject_data:
            this_subject = es.st_subject
            this_subject = replace_val(this_subject)
            this_functionTeam = es.st_team
            if this_subject not in subject_functionTeam_dic.keys():
                subject_functionTeam_dic[this_subject] = this_functionTeam
        functionTeam_edemand_dic = {}
        detail_data_dic = {}
        # edemand_obj = EDemand.objects.filter(d_application__year = 2017, d_status__in = [u'進行中',u'完成']) # Test
        for edemand in edemand_data:
            this_d_number = edemand.d_number
            this_d_department = edemand.d_department
            this_d_department = replace_val(this_d_department)

            # 招募、需求 详细信息
            get_ed_data = EDemand.objects.get(d_number__exact=this_d_number, d_status__in=[u'進行中', u'完成'])
            get_ed_list = [
                str(get_ed_data.d_application),
                get_ed_data.d_urgency, get_ed_data.d_number, get_ed_data.d_status,
                get_ed_data.d_bureau, get_ed_data.d_department,
                get_ed_data.d_abbreviation, get_ed_data.d_position, get_ed_data.d_amount,
                get_ed_data.d_finished, get_ed_data.d_offer, get_ed_data.d_unfinish,
                get_ed_data.d_requirement,
                get_ed_data.d_grade, get_ed_data.d_cellphone, get_ed_data.d_degree,
                get_ed_data.d_working, get_ed_data.d_demand01, get_ed_data.d_demand02,
                str(get_ed_data.d_register)
            ]
            d_amount = int(edemand.d_amount)  # 需求人數
            d_offer = 0  # 錄用人數
            # 计算招募状况为 完成 的数量  ? if...else 中的代码似乎一样
            get_recr_data = ERecruit.objects.filter(r_number=edemand.d_number, r_status__in=[u'進行中', u'已完成'])
            d_finished = 0  # 招募中
            get_recr_list = []
            for recr_data in get_recr_data:
                each_recr = [
                    str(recr_data.r_register), recr_data.r_status, recr_data.r_number,
                    recr_data.r_name, recr_data.r_sex, recr_data.r_contact,
                    str(recr_data.r_interview), recr_data.r_bureau, recr_data.r_department,
                    recr_data.r_position, recr_data.r_demand01, recr_data.r_degree,
                    recr_data.r_grade, recr_data.r_result01, recr_data.r_result02,
                    recr_data.r_progress, str(recr_data.r_healthcheck), recr_data.r_checkresult
                ]
                get_recr_list.append(each_recr)
                # 计算已完成数
                if recr_data.r_status == u'已完成' and recr_data.r_result02 == u'錄用' and recr_data.r_progress == u'報到':
                    d_finished += 1
                # 计算offer数
                elif recr_data.r_status == u'進行中' and recr_data.r_progress != u'報到' and recr_data.r_result02 == u'錄用':
                    d_offer += 1
            if edemand.d_status != u'完成':
                # 剩余需求
                d_requirement = d_amount - int(edemand.d_offer)
            # 招募未完成状态
            else:
                d_requirement = int(edemand.d_requirement)
            # 获取functionTeam的详细数据
            if this_d_department in subject_functionTeam_dic.keys():
                this_functionTeam = subject_functionTeam_dic[this_d_department]
                if this_functionTeam not in functionTeam_edemand_dic.keys():
                    detail_data_dic[this_functionTeam] = [[get_ed_list, get_recr_list]]
                    functionTeam_edemand_dic[this_functionTeam] = [d_amount, d_finished, d_offer, d_requirement]
                else:
                    temp_list = functionTeam_edemand_dic[this_functionTeam]
                    temp_list[0] = temp_list[0] + d_amount
                    temp_list[1] = temp_list[1] + d_finished
                    temp_list[3] = temp_list[3] + d_requirement
                    temp_list[2] = temp_list[0] - temp_list[1] - temp_list[3]
                    functionTeam_edemand_dic[this_functionTeam] = temp_list
                    detail_data_dic[this_functionTeam].append([get_ed_list, get_recr_list])
        team_list = []
        new_list = []
        # 获取team_list
        for leader in leader_data:
            for eh in EHumans.objects.all():
                if eh.h_ename == leader:
                    if eh.h_team not in team_list:
                        team_list.append(eh.h_team)
        # 获取new_list
        for team in team_list:
            for fed in functionTeam_edemand_dic.keys():
                if team == fed:
                    temp_dict = {}
                    temp_dict[team] = functionTeam_edemand_dic[team]
                    if temp_dict not in new_list:
                        new_list.append(temp_dict)

        detail_data_dic = json.dumps(detail_data_dic)
        # functionTeam_edemand_dic = json.dumps(functionTeam_edemand_dic)
        new_list = json.dumps(new_list)
        response = render_to_response('NPI_EERF/Recruit_state.html', {
            'username': username, 'user_cname': user_cname,
            'user_authority': user_authority, 'all_team_data': json.dumps(all_team_data),
            'new_list': new_list, "detail_data_dic": detail_data_dic
        })
        return response
    else:
        return HttpResponseRedirect('/login/')


def dimission(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    离职页面的3个图的数据 1.计算每个月的EERF处师级离职率及每个leader下离职人员详细信息 2.当前年度每个leader师级离职状况
    3.当前年度系统已提离职名单，并对离职原因分析（圆饼图）
    :param req:
    :return:
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        user_cname, user_authority = get_CnameAndAuthority(username)
        leavenum_data = []
        leave_leader_list = []
        empl_data = EEmployee.objects.filter(e_category__exact=u'常設').exclude(e_id__contains='TMP', e_grade__contains=u'員')
        for i, empl in enumerate(empl_data.filter(e_status__exact=u'離職', e_lastdate__year=datetime.date.today().year)):
            if empl.e_leader not in leave_leader_list and empl.e_leader:
                leave_leader_list.append(empl.e_leader)
        for leader_name in leave_leader_list:
            every_leader = {}
            every_leader['name'] = leader_name
            # 今年离职师级人数
            every_leader['num'] = empl_data.filter(e_status__exact=u'離職', e_lastdate__year=datetime.date.today().year,
                                                   e_leader__exact=leader_name).exclude(e_grade__contains=u'員').count()

            # leader下總人數 没有用到
            # every_leader['M_num'] = empl_data.filter(e_status__exact=u'離職', e_lastdate__year=datetime.date.today().year,
            #                                       e_leader__exact=leader_name).exclude(e_grade__contains=u'員').count()

            # leader下的总人数 在职的 + 今年内离职的师级人数
            every_leader['sum_number'] = empl_data.filter(e_status__exact=u'在職', e_leader__exact=leader_name).exclude(
                e_grade__contains=u'員').count() + every_leader['num']
            # print(leader_name, '---', every_leader['sum_number'], '---', every_leader['num'])
            # 离职率
            every_leader['leaveRate'] = float(every_leader['num']) / every_leader['sum_number']
            every_leader['specific_info'] = []
            for empl in empl_data.filter(e_status__exact=u'離職'
                    , e_lastdate__year=datetime.date.today().year
                    , e_leader__exact=leader_name).exclude(e_grade__contains=u'員').order_by("-e_lastdate"):
                leave_empl = {}
                leave_empl['id'] = empl.e_id
                leave_empl['name'] = empl.e_cname
                leave_empl['grade'] = empl.e_grade
                leave_empl['difference'] = empl.e_difference
                # if empl.e_seniority is None:
                #     leave_empl['seniority'] = 0
                # else:
                #     leave_empl['seniority'] = '%.2f' % empl.e_seniority
                d_emp = EDimission.objects.filter(d_number__exact=empl.e_id)
                if len(d_emp) > 0:
                    seniority = '%.2f' % d_emp[0].d_seniority
                else:
                    if empl.e_seniority is not None:
                        seniority = '%.2f' % empl.e_seniority
                    else:
                        seniority = 0
                leave_empl['seniority'] = seniority
                leave_empl['team'] = empl.e_functionteam
                leave_empl['leave_date'] = str(empl.e_lastdate)
                every_leader['specific_info'].append(leave_empl)
            if every_leader['num'] > 0:
                leavenum_data.append(every_leader)
        # 对 leaveRate 倒序排序
        leavenum_data.sort(key=lambda x: -x['leaveRate'])
        # get 离职率
        dimission_rate = []
        dimission_num = []
        dimission_zong = []
        for i, leave_data in enumerate(Eleaveprob.objects.all().order_by('l_datetime')):
            month_dimission_rate = []
            month_dimission_num = []
            # l.l_datetime.timetuple() 把datetime.date()格式转换成sequence  time.strftime("%b %Y",l.l_datetime.timetuple())
            # month_dimission_rate.append(int(time.mktime(l.l_datetime.timetuple()))*1000) #转成时间戳
            month_dimission_rate.append(str(leave_data.l_datetime))
            month_dimission_rate.append(float('%.2f' % leave_data.l_leaveprob))
            dimission_rate.append(month_dimission_rate)
            # leader下的月离职数据
            if Eleavenum.objects.filter(l_datetime__year=leave_data.l_datetime.year,
                                        l_datetime__month=leave_data.l_datetime.month):
                for leave in Eleavenum.objects.filter(l_datetime__year=leave_data.l_datetime.year,
                                                      l_datetime__month=leave_data.l_datetime.month):
                    month_leader_num = {}
                    month_leader_num['name'] = leave.l_leader

                    month_leader_num['shi'] = empl_data.filter(e_leader__exact=leave.l_leader, e_status__exact=u'在職',
                                                               e_grade__contains=u'師').count()
                    month_leader_num['num'] = leave.l_leavenum
                    month_leader_num['zong'] = (month_leader_num['num'] * 100.00) / month_leader_num['shi']
                    month_leader_num['speific_info'] = []
                    # 离职数据
                    for empl in empl_data.filter(e_leader__exact=leave.l_leader, e_status__exact=u'離職',
                                                 e_lastdate__year=leave_data.l_datetime.year,
                                                 e_lastdate__month=leave_data.l_datetime.month).exclude(
                        e_grade__contains=u'員').order_by("-e_lastdate"):
                        empl_info = {}
                        empl_info['id'] = empl.e_id
                        empl_info['name'] = empl.e_cname
                        empl_info['grade'] = empl.e_grade
                        empl_info['difference'] = empl.e_difference
                        # 计算离职率
                        # 离职人员年资为None的默认为0否则取2位小数
                        # if empl.e_seniority is None:
                        #     empl_info['seniority'] = 0
                        # else:
                        #     empl_info['seniority'] = '%.2f' % empl.e_seniority
                        d_emp_ = EDimission.objects.filter(d_number__exact=empl.e_id)
                        if len(d_emp_) > 0:
                            seniority_ = '%.2f' % d_emp_[0].d_seniority
                        else:
                            if empl.e_seniority is not None:
                                seniority_ = '%.2f' % empl.e_seniority
                            else:
                                seniority_ = 0
                        empl_info['seniority'] = seniority_
                        empl_info['team'] = empl.e_functionteam
                        empl_info['leave_date'] = str(empl.e_lastdate)
                        month_leader_num['speific_info'].append(empl_info)
                    if leave.l_leavenum != 0:
                        month_dimission_num.append(month_leader_num)
            month_dimission_num.sort(key=lambda x: -x['zong'])  # 对 x['zong'] 倒序排序
            dimission_num.append(month_dimission_num)

        # get 离职名单
        dimission_info = []
        reason_list = []
        for j, d in enumerate(
                EDimission.objects.filter(d_requestdate__year=datetime.date.today().year).order_by('-d_requestdate')):
            if d.d_reason01 != ' ':
                reason_list.append(d.d_reason01)
            if d.d_reason02 != ' ':
                reason_list.append(d.d_reason02)
            if d.d_reason03 != ' ':
                reason_list.append(d.d_reason02)
            # 每人的离职信息
            everyone_info = {}
            everyone_info['eid'] = d.d_number
            everyone_info['name'] = d.d_cname
            everyone_info['step'] = d.d_step
            everyone_info['seniority'] = d.d_seniority
            everyone_info['reason01'] = d.d_reason01
            everyone_info['grade'] = d.d_grade
            everyone_info['department'] = d.d_department
            everyone_info['reason02'] = d.d_reason02
            everyone_info['reason03'] = d.d_reason03
            dimission_info.append(everyone_info)

        key_word = [{u'工作因素': [u'不認同主管管理方式', u'工作壓力過大', u'缺乏晋升及發展機會', u'與同事相處不和諧', u'加班較多', u'工作志趣差異', u'不適應上夜班',
                               u'工作地點變更', u'工作重複單調、枯燥', u'工作崗位環境影響', u'考績評定不認可']},
                    {u'個人原因': [u'返鄉就業', u'照顧家人', u'自行創業', u'身體健康因素', u'親友不在身邊', u'返鄉結婚', u'轉換行業', u'請假未獲准',
                               u'達法定退休年齡']},
                    {u'不認同公司文化': [u'不認同公司文化']},
                    {u'薪資收入': [u'標準薪資低', u'加班少,收入比原來少', u'對獎金不滿意', u'被挖角']},
                    {u'生活環境': [u'周邊環境影響', u'對住宿不滿意', u'對伙食不滿意']},
                    {u'培訓機會少': [u'自我提升機會少']},
                    {u'企業經營情況影響': [u'生產淡季訂單減少', u'搬遷分流影響', u'組織調整']}]
        # 离职原因数据
        all_reason_data = []
        for dict in key_word:
            leave_reason_num = {}
            leave_reason_num['reason'] = dict.keys()[0]
            leave_reason_num['num'] = 0
            leave_reason_num['specific_reason_data'] = []
            for reason in reason_list:
                if reason in dict[dict.keys()[0]]:
                    leave_reason_num['num'] += 1
            for specific in dict[dict.keys()[0]]:
                each_specific = {}
                each_specific['specific_reason'] = specific
                each_specific['num'] = reason_list.count(specific)
                leave_reason_num['specific_reason_data'].append(each_specific)
            all_reason_data.append(leave_reason_num)

        response = render_to_response('NPI_EERF/Dimission_State.html',
                                      {'username': username, 'user_cname': user_cname, 'user_authority': user_authority,
                                       'leave_num_data': json.dumps(leavenum_data),
                                       'dimission_rate': json.dumps(dimission_rate), 'dimission_info': dimission_info,
                                       'dimission_num': json.dumps(dimission_num),
                                       'dimission_zong': json.dumps(dimission_zong),
                                       'all_reason_data': json.dumps(all_reason_data)})
        return response
    else:
        return HttpResponseRedirect('/login/')


def overwork(req):
    """
    工作超时人数计算
    :param req:
    :return:超时加班leader
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        user_cname, user_authority = get_CnameAndAuthority(username)
        etimeout_data = EGreaterthan.objects.all().order_by("g_datetime")
        section_timeout_data = ESectionGreaterthan.objects.all().order_by("g_datetime")
        etimeout_leader_dic = {}
        etimeout_section_dic = {}
        # 所有超时加班列表 -- 部级
        for time in etimeout_data:
            this_db_datetime = str(time.g_datetime)
            this_db_leader = time.g_leader
            this_db_all_over_list = [float(time.g_9_hours), float(time.g_9_5_hours),
                                     float(time.g_10_hours), float(time.g_10_5_hours), float(time.g_11_hours)]
            if this_db_leader not in etimeout_leader_dic.keys():
                etimeout_leader_dic[this_db_leader] = [[this_db_datetime, this_db_all_over_list]]
            else:
                this_key_value_list = [this_db_datetime, this_db_all_over_list]
                etimeout_leader_dic[this_db_leader].append(this_key_value_list)

        # 所有超时加班列表 -- 科级
        for time in section_timeout_data:
            this_db_datetime = str(time.g_datetime)
            this_db_section = time.g_section
            this_db_all_over_list = [float(time.g_9_hours), float(time.g_9_5_hours),
                                     float(time.g_10_hours), float(time.g_10_5_hours), float(time.g_11_hours)]
            if this_db_section not in etimeout_section_dic.keys():
                etimeout_section_dic[this_db_section] = [[this_db_datetime, this_db_all_over_list]]
            else:
                this_key_value_list = [this_db_datetime, this_db_all_over_list]
                etimeout_section_dic[this_db_section].append(this_key_value_list)

        # leaders
        AllLeaders = json.dumps(get_leader())

        response = render_to_response('NPI_EERF/Overwork.html', {'username': username, 'user_cname': user_cname,
                                                                 'user_authority': user_authority,
                                                                 "etimeout_leader_dic": json.dumps(etimeout_leader_dic),
                                                                 "etimeout_section_dic": json.dumps(etimeout_section_dic),
                                                                 'AllLeaders': AllLeaders})
        return response
    else:
        return HttpResponseRedirect('/login/')


def parse_date_str(date_str):
    if date_str:
        date_list = date_str.split(':')
        hh = int(date_list[0])
        mm = int(date_list[1])
        ss = int(date_list[2])
        return hh * 3600 + mm * 60 + ss
    else:
        return 0


def parse_date_str_2(date_str):
    if date_str:
        date_list = date_str.split(':')
        hh = int(date_list[0])
        mm = int(date_list[1])
        ss = int(date_list[2])
        if hh == 0:
            return 86400 + mm * 60 + ss
        else:
            return hh * 3600 + mm * 60 + ss
    else:
        return 0

global_section_list = []
@csrf_exempt
def work_ajax(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    考勤模块4个页面第三层的科级数据，根据前台传递的参数返回对应的leader下所有科级的考勤数据
    :param req:
    :return: querysetList
    """
    #  根据部门编号获取 每个部门的leader
    leaders = get_leader()
    # 部门索引
    leader_index = int(req.POST.get('leaderIndex'))
    # 取出对应部级英文名
    selected_leader = leaders[leader_index]
    year = req.POST.get('year')
    month = req.POST.get('month')

    # 找出每一个对应部级下的人对象
    _obj = EAttendance.objects.filter(a_leader__exact=selected_leader, a_datetime__year=year, a_datetime__month=month)

    # 科级名字典
    section_list = []
    for each_obj in _obj:
        # 科级名
        leader_obj = EEmployee.objects.get(e_id__exact=each_obj.a_employee)
        if leader_obj.e_leader == selected_leader:
            section_name = leader_obj.e_functionteam
            # 写入字典
            if section_name:
                if section_name not in section_list:
                    # print section_name
                    section_list.append(section_name)
    global global_section_list
    global_section_list = []
    global_section_list = section_list

    return HttpResponse(json.dumps(section_list, cls=DjangoJSONEncoder, ensure_ascii=False))


@csrf_exempt
def work_section_ajax(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    考勤模块4个页面第四层的模态框表格数据，根据前台传递的参数返回对应的科级下所有人的根据所有字段排序的数据
    :param req:
    :return: querysetList
    """
    # print global_section_list
    # 获取 每个部门下的科级列表
    section_list = global_section_list

    # 科级索引
    section_index = int(req.POST.get('leaderIndex'))
    # 取出对应部级英文名
    selected_section = section_list[section_index]
    year = req.POST.get('year')
    month = req.POST.get('month')

    _obj = EEmployee.objects.filter(e_functionteam=selected_section, e_status__exact=u'在職')
    new_list = []
    for i in _obj:
        # 员工工号
        try:
            each_obj = EAttendance.objects.get(a_employee__exact=i.e_id, a_datetime__year=year, a_datetime__month=month)
        except:
            # print "%s在EAttendance表中不存在" %(i.e_id)
            continue

        # 部长工号列表
        leader_num = EDepartment.objects.values('d_leadernum')
        leader_num_list = []
        for i in leader_num:
            leader_num_id = i['d_leadernum']
            if leader_num_id not in leader_num_list:
                leader_num_list.append(leader_num_id)
        # 判断是否是部长, 是的话去除
        if each_obj.a_employee in leader_num_list:
            continue

        new_obj = {}
        new_obj['a_employee'] = each_obj.a_employee
        new_obj['a_name'] = each_obj.a_name

        new_obj['a_avgdutyhours'] = each_obj.a_avgdutyhours
        new_obj['a_avghours'] = each_obj.a_avghours
        new_obj['a_avglastcard'] = each_obj.a_avglastcard
        new_obj['a_avgoverhours'] = each_obj.a_avgoverhours
        new_obj['a_dutydays'] = each_obj.a_dutydays

        new_obj['a_maxdutyhours'] = each_obj.a_maxdutyhours
        new_obj['a_maxhours'] = each_obj.a_maxhours
        new_obj['a_maxlastcard'] = each_obj.a_maxlastcard
        new_obj['a_maxoverhours'] = each_obj.a_maxoverhours

        new_obj['a_nightnum'] = each_obj.a_nightnum
        new_obj['a_totaldays'] = each_obj.a_totaldays
        new_obj['a_totaldutyhours'] = each_obj.a_totaldutyhours
        new_obj['a_totalhours'] = each_obj.a_totalhours
        new_obj['a_totaloverhours'] = each_obj.a_totaloverhours
        new_obj['a_offduty'] = each_obj.a_offduty
        new_obj['a_unoffduty'] = each_obj.a_unoffduty
        per_total = float(each_obj.a_offduty) + float(each_obj.a_unoffduty)
        if each_obj.a_offduty and per_total:
            new_obj['a_offdutyper'] = round(float(each_obj.a_offduty) * 100 / per_total, 2)
        else:
            new_obj['a_offdutyper'] = 0
        if each_obj.a_unoffduty and per_total:
            new_obj['a_unoffdutyper'] = round(float(each_obj.a_unoffduty) * 100 / per_total, 2)
        else:
            new_obj['a_unoffdutyper'] = 0
        new_list.append(new_obj)

    a_avgdutyhours_data = sorted(new_list, key=lambda x: (x['a_avgdutyhours']), reverse=True)

    a_avghours_data = sorted(new_list, key=lambda x: (x['a_avghours']), reverse=True)

    a_avglastcard_data = sorted(new_list, key=lambda x: (x['a_avglastcard']), reverse=True)

    a_avgoverhours_data = sorted(new_list, key=lambda x: (x['a_avgoverhours']), reverse=True)

    a_dutydays_data = sorted(new_list, key=lambda x: (x['a_dutydays']), reverse=True)

    # 最大义务时长
    a_maxdutyhours_data = sorted(new_list, key=lambda x: (x['a_maxdutyhours']), reverse=True)

    # 最大工作时长 排序有问题
    a_maxhours_data = sorted(new_list, key=lambda x: (x['a_maxhours']), reverse=True)

    # 最晚白班下班时间
    a_maxlastcard_data = sorted(new_list, key=lambda x: (parse_date_str_2(x['a_maxlastcard'])), reverse=True)

    # 最大超时时长
    a_maxoverhours_data = sorted(new_list, key=lambda x: (x['a_maxoverhours']), reverse=True)

    a_nightnum_data = sorted(new_list, key=lambda x: (x['a_nightnum']), reverse=True)

    a_totaldays_data = sorted(new_list, key=lambda x: (x['a_totaldays']), reverse=True)

    a_totaldutyhours_data = sorted(new_list, key=lambda x: (x['a_totaldutyhours']), reverse=True)

    a_totalhours_data = sorted(new_list, key=lambda x: (x['a_totalhours']), reverse=True)

    a_totaloverhours_data = sorted(new_list, key=lambda x: (x['a_totaloverhours']), reverse=True)

    a_offduty_data = sorted(new_list, key=lambda x: (x['a_offduty']), reverse=True)

    a_unoffduty_data = sorted(new_list, key=lambda x: (x['a_unoffduty']), reverse=True)

    a_offdutyper_data = sorted(new_list, key=lambda x: (x['a_offdutyper']), reverse=True)

    a_unoffdutyper_data = sorted(new_list, key=lambda x: (x['a_unoffdutyper']), reverse=True)

    alldata = {}
    alldata['a_avgdutyhours'] = a_avgdutyhours_data
    alldata['a_avghours'] = a_avghours_data
    alldata['a_avglastcard'] = a_avglastcard_data
    alldata['a_avgoverhours'] = a_avgoverhours_data
    alldata['a_dutydays'] = a_dutydays_data
    alldata['a_maxdutyhours'] = a_maxdutyhours_data
    alldata['a_maxhours'] = a_maxhours_data
    alldata['a_maxlastcard'] = a_maxlastcard_data
    alldata['a_maxoverhours'] = a_maxoverhours_data
    alldata['a_nightnum'] = a_nightnum_data
    alldata['a_totaldays'] = a_totaldays_data
    alldata['a_totaldutyhours'] = a_totaldutyhours_data
    alldata['a_totalhours'] = a_totalhours_data
    alldata['a_totaloverhours'] = a_totaloverhours_data
    alldata['a_offduty'] = a_offduty_data
    alldata['a_unoffduty'] = a_unoffduty_data
    alldata['a_offdutyper'] = a_offdutyper_data
    alldata['a_unoffdutyper'] = a_unoffdutyper_data

    return HttpResponse(json.dumps(alldata, cls=DjangoJSONEncoder, ensure_ascii=False))


def overtimework(req):
    """
    超时加班时数
    :param req:
    :return:超时加班时数
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        user_cname, user_authority = get_CnameAndAuthority(username)
        edutywork_obj = EDutywork.objects.all().order_by("d_datetime")
        sectionwork_obj = ESectionDutywork.objects.all().order_by("d_datetime")
        edutywork_leader_dic = {}
        edutywork_year_list = []

        sectionwork_leader_dic = {}
        sectionwork_year_list = []
        # 获取leader 超时加班的数据
        for ed in edutywork_obj:
            # 生成該筆數據的日期
            this_db_datetime = str(ed.d_datetime)
            # 部级领导英文名
            this_db_leader = ed.d_leader
            # 超时加班平均人次
            this_db_d_number = float(ed.d_number)
            # 生成該筆數據的日期 --> 写入列表
            if this_db_datetime not in edutywork_year_list:
                edutywork_year_list.append(this_db_datetime)
            # 部级领导英文名 --> 写入字典
            if this_db_leader not in edutywork_leader_dic.keys():
                                    # 部级领导英文名: [生成該筆數據的日期, 超时加班平均人次]
                edutywork_leader_dic[this_db_leader] = [[this_db_datetime, this_db_d_number]]
            else:
                # 存在添加
                this_key_value_list = [this_db_datetime, this_db_d_number]
                edutywork_leader_dic[this_db_leader].append(this_key_value_list)

        # leaders  根据部门编号获取 每个部门的leader
        AllLeaders = json.dumps(get_leader())
        # 获取科级 超时加班的数据
        for ed in sectionwork_obj:
            # 生成該筆數據的日期
            this_db_datetime = str(ed.d_datetime)
            # 科名
            this_db_leader = ed.d_section
            # 超时加班平均人次
            this_db_d_number = float(ed.d_number)
            # 生成該筆數據的日期 --> 写入列表
            if this_db_datetime not in sectionwork_year_list:
                sectionwork_year_list.append(this_db_datetime)
            # 科级id --> 写入字典
            if this_db_leader not in sectionwork_leader_dic.keys():
                # 部级领导英文名: [生成該筆數據的日期, 超时加班平均人次]
                sectionwork_leader_dic[this_db_leader] = [[this_db_datetime, this_db_d_number]]
            else:
                # 存在添加
                this_key_value_list = [this_db_datetime, this_db_d_number]
                sectionwork_leader_dic[this_db_leader].append(this_key_value_list)

        response = render_to_response('NPI_EERF/Overtimework.html', {'username': username, 'user_cname': user_cname,
                                                                     'user_authority': user_authority,
                                                                     "edutywork_year_list": json.dumps(
                                                                         edutywork_year_list),
                                                                     "edutywork_leader_dic": json.dumps(
                                                                         edutywork_leader_dic),
                                                                     "AllLeaders": AllLeaders,

                                                                     "sectionwork_year_list": json.dumps(
                                                                         sectionwork_year_list),
                                                                     "sectionwork_leader_dic": json.dumps(
                                                                         sectionwork_leader_dic),
                                                                     },)
        return response
    else:
        return HttpResponseRedirect('/login/')


def reportform(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    报表的人力超时状态 ：动态的级联选择框
    :param req:
    :return:team列表
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        # 部级id列表
        team_obj = ETeam.objects.all()
        eleader_obj = ELeader.objects.all().order_by("edepartment_num")
        edepartment_num_list = []
        for leader in eleader_obj:
            if leader.edepartment_num not in edepartment_num_list:
                edepartment_num_list.append(leader.edepartment_num)
        # 获取team_list数据
        leaders_list = get_leader()
        team_list = []
        for depa_num in edepartment_num_list:
            temp_dict = {}
            temp_dict['leader'] = leaders_list[depa_num]
            temp_dict['team'] = []
            for leader_data in eleader_obj.filter(edepartment_num__exact=depa_num):
                for each_team in team_obj.filter(eleader_id__exact=leader_data.l_id):
                    temp_dict['team'].append(each_team.t_team)
            team_list.append(temp_dict)

        response = render_to_response('NPI_EERF/ReportForm.html', {'username': username, 'leaders_list': leaders_list,
                                                                   'sorted_team_list': json.dumps(team_list)})
        return response
    else:
        return HttpResponseRedirect('/login/')


@csrf_exempt
def report_message_second(req):
    """
    人力基础总表
    :param req:
    :return:
    """
    if req.POST:
        get_html_time = req.POST.get('_time')
        get_html_time_list = get_html_time.split('-')
        get_time = datetime.datetime.strptime(get_html_time, "%Y-%m-%d")
        # try:
        all_emp_dic = {}
        emp_data = EEmployee.objects.filter(e_status__exact=u"在職").exclude(e_adduser__exact='add',
                                                                           e_status__exact=u"離職",
                                                                           e_lastdate__lt=get_time)
        for emp in emp_data:
            this_man_number = str(emp.e_id)
            each_emp_data = []
            each_emp_data.append(this_man_number)
            each_emp_data.append(emp.e_cname)
            each_emp_data.append(emp.e_grade)
            each_emp_data.append(emp.e_difference)
            each_emp_data.append(emp.e_management)
            each_emp_data.append(emp.e_managers)
            each_emp_data.append(emp.e_functionteam)
            each_emp_data.append(emp.e_category)
            each_emp_data.append(emp.e_degree)
            each_emp_data.append(str(emp.e_firstdate))
            if emp.e_seniority:
                each_emp_data.append(round(emp.e_seniority, 2))
            else:
                each_emp_data.append(0)
            if emp.edepartment_id:
                each_emp_data.append(emp.edepartment.d_department)
            else:
                each_emp_data.append("")
            if emp.esubject:
                # 將FATP Data中的 認證規範部_觀瀾 iDPBG 改為 數據統合部_觀瀾
                if emp.esubject.s_subject == u'iDPBG EERF FATP 軟件開發課_觀瀾':
                    dep_index = each_emp_data.index(emp.edepartment.d_department)
                    each_emp_data[dep_index] = u"iDPBG 數據統合部_觀瀾"
                each_emp_data.append(emp.esubject.s_subject)
            else:
                each_emp_data.append("")
            each_emp_data.append(emp.e_email)
            each_emp_data.append(emp.e_phone)
            each_emp_data.append(emp.e_cellphone)

            erest_data = ERest.objects.filter(r_employee=this_man_number, r_datetime__year=get_html_time_list[0],
                                              r_datetime__month=(int(get_html_time_list[1]) - 1))
            # 获取调休数据
            if erest_data:
                erest_data = erest_data[0]
                each_emp_data.append(round(erest_data.r_effectivity01, 4))
                each_emp_data.append(round(erest_data.r_overtime01, 4))
                each_emp_data.append(round(erest_data.r_rest01, 4))
                each_emp_data.append(round(erest_data.r_effectivity02, 4))
                each_emp_data.append(round(erest_data.r_overtime02, 4))
                each_emp_data.append(round(erest_data.r_rest02, 4))
                each_emp_data.append(round(erest_data.r_effectivity03, 4))
                each_emp_data.append(round(erest_data.r_nightshift, 4))
                each_emp_data.append(round(erest_data.r_totalrest, 4))
            else:
                each_emp_data.append(0)
                each_emp_data.append(0)
                each_emp_data.append(0)
                each_emp_data.append(0)
                each_emp_data.append(0)
                each_emp_data.append(0)
                each_emp_data.append(0)
                each_emp_data.append(0)
                each_emp_data.append(0)
            all_emp_dic[this_man_number] = each_emp_data

        return HttpResponse(json.dumps(all_emp_dic))


@csrf_exempt
def report_anomaly(req):
    """

    :param req:
    :return: 考勤异常数据
    """
    if req.POST:
        leader = req.POST.get('selectedLeader')
        team = req.POST.get('selectedTeam')
        if leader == 'All':
            search_yesr = datetime.datetime.now().year
            search_month = datetime.datetime.now().month
            eattendanceanomaly_obj = EATTENDANCEANOMALY.objects.filter(a_datetime__year=search_yesr, a_datetime__month=search_month).order_by("a_employeeid")
            eattendanceanomaly_list = list(eattendanceanomaly_obj.values())
            a = 0
            for i in eattendanceanomaly_obj:
                if i.a_lastcard:
                    eattendanceanomaly_list[a]['a_lastcard'] = i.a_lastcard.strftime('%Y-%m-%d %H:%M:%S')
                if i.a_firstcrad:
                    eattendanceanomaly_list[a]['a_firstcrad'] = i.a_firstcrad.strftime('%Y-%m-%d %H:%M:%S')
                a += 1
            return HttpResponse(json.dumps(eattendanceanomaly_list, cls=DjangoJSONEncoder, ensure_ascii=False))
        elif team == 'All':
            search_yesr = datetime.datetime.now().year
            search_month = datetime.datetime.now().month
            eattendanceanomaly_obj = EATTENDANCEANOMALY.objects.filter(a_datetime__year=search_yesr,
                                                                       a_datetime__month=search_month).order_by(
                "a_employeeid")
            eattendanceanomaly_list = list(eattendanceanomaly_obj.values())
            a = 0
            for i in eattendanceanomaly_obj:
                if i.a_lastcard:
                    eattendanceanomaly_list[a]['a_lastcard'] = i.a_lastcard.strftime('%Y-%m-%d %H:%M:%S')
                if i.a_firstcrad:
                    eattendanceanomaly_list[a]['a_firstcrad'] = i.a_firstcrad.strftime('%Y-%m-%d %H:%M:%S')
                a += 1
            team_obj = ETeam.objects.filter(t_leader=leader)
            team_list = []
            for j in team_obj:
                team_list.append(j.t_team)
            eattendanceanomaly_list1 = []
            for k in  eattendanceanomaly_list:
                if k['a_class'] in team_list:
                    eattendanceanomaly_list1.append(k)

            return HttpResponse(json.dumps(eattendanceanomaly_list1, cls=DjangoJSONEncoder, ensure_ascii=False))
        else:
            search_yesr = datetime.datetime.now().year
            search_month = datetime.datetime.now().month
            eattendanceanomaly_obj = EATTENDANCEANOMALY.objects.filter(a_datetime__year=search_yesr,
                                                                       a_datetime__month=search_month, a_class=team).order_by(
                "a_employeeid")
            eattendanceanomaly_list = list(eattendanceanomaly_obj.values())
            a = 0
            for i in eattendanceanomaly_obj:
                if i.a_lastcard:
                    eattendanceanomaly_list[a]['a_lastcard'] = i.a_lastcard.strftime('%Y-%m-%d %H:%M:%S')
                if i.a_firstcrad:
                    eattendanceanomaly_list[a]['a_firstcrad'] = i.a_firstcrad.strftime('%Y-%m-%d %H:%M:%S')
                a += 1
            return HttpResponse(json.dumps(eattendanceanomaly_list, cls=DjangoJSONEncoder, ensure_ascii=False))


@csrf_exempt
def get_bonus_report(req):
    get_id = req.POST.get("checked_id")
    bonus_obj_team = EBONUSREPORT.objects.filter(b_uuid__exact=get_id, b_datatype__exact='team')
    response_data = {}
    for i in bonus_obj_team:
        response_data[i.b_team] = [i.b_id, i.b_leader, i.b_teamleader, i.b_hr, i.b_gsnum, i.b_gsweight, i.b_gsrate, i.b_patent, i.b_patentweight, i.b_patentrate, i.b_tax, i.b_taxweight, i.b_proposal, i.b_ee, i.b_eepoint, i.b_idl, i.b_customer, i.b_dutywork, i.b_dutyworkhc, i.b_over10_5, i.b_over10_5hc, i.b_night, i.b_nighthc, i.b_travelabroad, i.b_travelabroadhc, i.b_travelcn, i.b_travelcnhc, i.b_leaveprob, i.b_leavepoint, i.b_leaverate, i.b_attendance, i.b_other, i.b_taskforcenum, i.b_taskforce, i.b_total, i.b_money, i.b_violation, i.b_belowquality, i.b_finalymoney,i.b_teamloading]
        response_data[i.b_team].append(EEmployee.objects.filter(e_category__exact=u'常設', e_functionteam__exact=i.b_team, e_status__exact=u'在職', e_grade__contains=u'師').exclude(e_id__contains='TMP',e_grade__contains=u'員').count())
    bonus_obj_department = EBONUSREPORT.objects.filter(b_uuid__exact=get_id, b_datatype__exact='department')

    for i in bonus_obj_department:
        try:
            response_data[i.b_leader] = [i.b_id, i.b_leader, i.b_teamleader, i.b_hr, i.b_gsnum, i.b_gsweight, i.b_gsrate, i.b_patent, i.b_patentweight, i.b_patentrate, i.b_tax, i.b_taxweight, i.b_proposal, i.b_ee, i.b_eepoint, i.b_idl, i.b_customer, i.b_dutywork, i.b_dutyworkhc, i.b_over10_5, i.b_over10_5hc, i.b_night, i.b_nighthc, i.b_travelabroad, i.b_travelabroadhc, i.b_travelcn, i.b_travelcnhc, i.b_leaveprob, i.b_leavepoint, i.b_leaverate, i.b_attendance, i.b_other, i.b_taskforcenum, i.b_taskforce, i.b_total, i.b_money, i.b_violation, i.b_belowquality, i.b_finalymoney,i.b_teamloading,i.b_totalpercentage_lastyear, i.b_totalmoney_lastyear]
            response_data[i.b_leader].append(EEmployee.objects.filter(e_category__exact=u'常設', e_leader=i.b_leader, e_status__exact=u'在職', e_grade__contains=u'師').exclude(e_id__contains='TMP',e_grade__contains=u'員').count())
        except Exception as e:
            print(e)

    response_data["team_name"] = list(bonus_obj_team.values("b_team"))
    response_data["department"] = list(bonus_obj_department.values("b_leader"))

    bp_obj = EBONUSPERCENTAGE.objects.filter(bp_uuid__exact=get_id)[0]
    response_data['bp_totalmoney'] = bp_obj.bp_totalmoney
    response_data['bp_personalmoney'] = bp_obj.bp_personalmoney
    response_data['bp_teammoney'] = bp_obj.bp_teammoney
    response_data['bp_othermoney'] = bp_obj.bp_othermoney
    response_data["bp_otherper_t"] = bp_obj.bp_otherper_t
    response_data["bp_otherper_d"] = bp_obj.bp_otherper_d
    response_data["bp_taskforceper_t"] = bp_obj.bp_taskforceper_t
    response_data["bp_taskforceper_d"] = bp_obj.bp_taskforceper_d
    response_data["bp_hrper_d"] = bp_obj.bp_hrper_d
    response_data["bp_proposal_t"] = bp_obj.bp_proposal_t
    response_data["bp_proposal_d"] = bp_obj.bp_proposal_d
    response_data["bp_ee_t"] = bp_obj.bp_ee_t
    response_data["bp_ee_d"] = bp_obj.bp_ee_d
    response_data["bp_idl_t"] = bp_obj.bp_idl_t
    response_data["bp_idl_d"] = bp_obj.bp_idl_d
    response_data["bp_duty_t"] = bp_obj.bp_duty_t
    response_data["bp_duty_d"] = bp_obj.bp_duty_d
    response_data["bp_10_5_t"] = bp_obj.bp_10_5_t
    response_data["bp_10_5_d"] = bp_obj.bp_10_5_d
    response_data["bp_night_t"] = bp_obj.bp_night_t
    response_data["bp_night_d"] = bp_obj.bp_night_d
    response_data["bp_travel_abroad_t"] = bp_obj.bp_travel_abroad_t
    response_data["bp_travel_abroad_d"] = bp_obj.bp_travel_abroad_d
    response_data["bp_travel_cn_t"] = bp_obj.bp_travel_cn_t
    response_data["bp_travel_cn_d"] = bp_obj.bp_travel_cn_d
    response_data["bp_leave_t"] = bp_obj.bp_leave_t
    response_data["bp_leave_d"] = bp_obj.bp_leave_d
    response_data["bp_gsweight_t"] = bp_obj.bp_gsweight_t
    response_data["bp_gsweight_d"] = bp_obj.bp_gsweight_d
    response_data["bp_patentweight_t"] = bp_obj.bp_patentweight_t
    response_data["bp_patentweight_d"] = bp_obj.bp_patentweight_d
    response_data["bp_taxweight_t"] = bp_obj.bp_taxweight_t
    response_data["bp_taxweight_d"] = bp_obj.bp_taxweight_d

    return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder, ensure_ascii=False))


@csrf_exempt
def del_bonus(req):
    del_id = req.POST.get("checked_id").split("@@")[1:]
    now_date = datetime.datetime.now()
    for id in del_id:
        EBONUSREPORT.objects.filter(b_uuid__exact=id).update(b_deldate=now_date)
    return HttpResponse(json.dumps({"result":"succeed"}, cls=DjangoJSONEncoder, ensure_ascii=False))



@csrf_exempt
def get_table_info(req):
    bonus_obj = list(set(map(lambda x:(x["b_tablename"], x["b_datetime"], x["b_uuid"]),EBONUSREPORT.objects.filter(b_deldate__isnull=True).values("b_tablename","b_datetime","b_uuid"))))
    bonus_obj.sort(key=lambda x: x[1],reverse = True)
    data = {"data":bonus_obj}
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder, ensure_ascii=False))


@csrf_exempt
def save_bonus(req):
    team_list = map(lambda x: x['t_team'], ETeam.objects.values('t_team'))
    team_list.append(u"ES")
    team_data_list = []
    now_time = datetime.datetime.now()
    info = req.POST.get("info")
    table_id = uuid.uuid1()
    table_id = "".join(str(table_id).split("-"))
    leader_list = get_leader()
    leader_list.append(u'Shirley')
    for leader in leader_list:
        value = req.POST.get(leader).split("@@")[1:]
        value.insert(0, "")
        value.insert(2, "")
        teamloading = value[31]
        del value[31]
        value.append(teamloading)
        try:
            EBONUSREPORT.objects.create(b_team=value[0], b_leader=value[1], b_teamleader=value[2], b_hr=value[3],
                                        b_gsnum=int(float(value[4])), b_gsweight=float(value[5]), b_gsrate=value[6],
                                        b_patent=int(float(value[7])), b_patentweight=float(value[8]), b_patentrate=value[9],
                                        b_tax=int(float(value[10])), b_taxweight=float(value[11]), b_proposal=value[12],
                                        b_ee=int(float(value[13])), b_eepoint=float(value[14]), b_idl=int(float(value[15])),
                                        b_customer=value[16], b_dutywork=float(value[17]),
                                        b_dutyworkhc=float(value[18]), b_over10_5=float(value[19]),
                                        b_over10_5hc=float(value[20]), b_night=float(value[21]),
                                        b_nighthc=float(value[22]), b_travelabroad=float(value[23]),
                                        b_travelabroadhc=float(value[24]), b_travelcn=float(value[25]),
                                        b_travelcnhc=float(value[26]), b_leaveprob=value[27],
                                        b_leavepoint=float(value[28]), b_leaverate=value[29], b_attendance=value[30],
                                        b_other=value[31], b_taskforcenum=int(float(value[32])), b_taskforce=value[33],
                                        b_total=value[34], b_money=float(value[35]), b_violation=float(value[40]),
                                        b_belowquality=float(value[41]), b_finalymoney=float(value[42]), b_datetime=now_time, b_tablename=info, b_uuid=table_id, b_datatype="department",b_teamloading=value[43],b_totalpercentage_lastyear=value[38],b_totalmoney_lastyear=value[39])
        except Exception as e:
            print(e)
    for team in team_list:
        if team == 'Inventory':
            continue
        team = team.replace("&", "&amp;")
        value = req.POST.get(team).split("@@")[1:]
        value[0].replace("&amp;", "&")
        value.insert(3, "")
        teamloading = value[31]
        del value[31]
        value.append(teamloading)
        try:
            EBONUSREPORT.objects.create(b_team=value[0], b_leader=value[1], b_teamleader=value[2], b_hr=value[3],
                                        b_gsnum=int(float(value[4])), b_gsweight=float(value[5]), b_gsrate=value[6],
                                        b_patent=int(float(value[7])), b_patentweight=float(value[8]), b_patentrate=value[9],
                                        b_tax=int(float(value[10])), b_taxweight=float(value[11]), b_proposal=value[12],
                                        b_ee=int(float(value[13])), b_eepoint=float(value[14]), b_idl=int(float(value[15])),
                                        b_customer=value[16], b_dutywork=float(value[17]),
                                        b_dutyworkhc=float(value[18]), b_over10_5=float(value[19]),
                                        b_over10_5hc=float(value[20]), b_night=float(value[21]),
                                        b_nighthc=float(value[22]), b_travelabroad=float(value[23]),
                                        b_travelabroadhc=float(value[24]), b_travelcn=float(value[25]),
                                        b_travelcnhc=float(value[26]), b_leaveprob=value[27],
                                        b_leavepoint=float(value[28]), b_leaverate=value[29], b_attendance=value[30],
                                        b_other=value[31], b_taskforcenum=int(float(value[32])), b_taskforce=value[33],
                                        b_total=value[34], b_money=float(value[35]), b_violation=float(value[40]),
                                        b_belowquality=float(value[41]), b_finalymoney=float(value[42]), b_datetime=now_time, b_tablename=info, b_uuid=table_id, b_datatype="team",b_teamloading=value[43])
        except Exception as e:
            print(e)
    try:
        EBONUSPERCENTAGE.objects.create(bp_totalmoney = float(req.POST.get("total_money")), bp_personalmoney = float(req.POST.get("personal_money")), bp_teammoney = float(req.POST.get("team_money")), bp_othermoney = float(req.POST.get("other_money")), bp_gsweight_t = float(req.POST.get("gs_weight_t")), bp_gsweight_d = float(req.POST.get("gs_weight_d")), bp_patentweight_t = float(req.POST.get("patent_weight_t")), bp_patentweight_d = float(req.POST.get("patent_weight_d")), bp_taxweight_t = float(req.POST.get("tax_weight_t")), bp_taxweight_d = float(req.POST.get("tax_weight_d")), bp_otherper_t = req.POST.get("other_t"), bp_otherper_d = req.POST.get("other_d"), bp_taskforceper_t = req.POST.get("task_force_t"), bp_taskforceper_d = req.POST.get("task_force_d"), bp_hrper_d = req.POST.get("hr_d"), bp_proposal_t = req.POST.get("proposal_t"), bp_proposal_d = req.POST.get("proposal_d"), bp_ee_t = req.POST.get("ee_t"), bp_ee_d = req.POST.get("ee_d"), bp_idl_t = req.POST.get("idl_t"), bp_idl_d = req.POST.get("idl_d"), bp_duty_t = req.POST.get("duty_t"), bp_duty_d = req.POST.get("duty_d"), bp_10_5_t = req.POST.get("10_5_t"), bp_10_5_d = req.POST.get("10_5_d"), bp_night_t = req.POST.get("night_d"), bp_night_d = req.POST.get("night_d"), bp_travel_abroad_t = req.POST.get("travel_abroad_t"), bp_travel_abroad_d = req.POST.get("travel_abroad_d"), bp_travel_cn_t = req.POST.get("travel_cn_t"), bp_travel_cn_d = req.POST.get("travel_cn_d"), bp_leave_t = req.POST.get("leave_t"), bp_leave_d = req.POST.get("leave_d"), bp_uuid = table_id )
    except Exception as e:
        print(e)

    return HttpResponse(json.dumps({"result": "succeed"}, cls=DjangoJSONEncoder, ensure_ascii=False))
        # print(value)
    # print(team_data_list)



@csrf_exempt
def table_score(req):

    username = req.COOKIES.get('eerf_user', '')
    if username:
        user = EEmployee.objects.get(e_id__exact=username)
        user_cname = user.e_cname
        user_authority = user.e_management
        user_chmod = user.e_chmod
        # 判断权限
        if user.e_chmod != 'admin':
            message = '權限不足'
            response = render_to_response('NPI_EERF/index.html',
                                          {'user_cname': user_cname, 'user_authority': user_authority,'message': message,
                                           'user_chmod': user_chmod}, context_instance=RequestContext(req))
            #         response.set_cookie('eerf_user',username,3600)
            return response
    else:
        return HttpResponseRedirect('/login/')

    if datetime.datetime.now().month > 3:
        gs_year = str(datetime.datetime.now().year)
    else:
        gs_year = str(datetime.datetime.now().year - 1)

    leader_list = get_leader()
    bonus_list = []
    bonus_list_by_leader = []

    total_gs_num = 0
    total_duty_work = 0
    total_over_10_5 = 0
    total_night_work = 0
    total_travel_cn = 0
    total_travel_abroad = 0
    total_leave_prob = round(Eleaveprob.objects.filter(l_datetime__gt=(datetime.datetime.now()-relativedelta(months=13)), l_datetime__lte=(datetime.datetime.now()-relativedelta(months=1))).aggregate(leave_prob_out = Sum('l_leaveprob'))['leave_prob_out'],2)
    leave_prob_max = 0.0
    leave_prob_max_department = 0.0
    team_id = 0
    user_mode = 1
    if username == "14484":
        user_mode = 0
    for leader in leader_list:
            team_id += 1
            # 總人口
            total_people = EEmployee.objects.filter(e_category__exact=u'常設', e_leader__exact=leader, e_status__exact=u'在職', e_grade__contains=u'師').exclude(e_id__contains='TMP',e_grade__contains=u'員').count()
            if total_people == 0:
                continue

            # 離職率
            leave_num = EEmployee.objects.filter(e_category__exact=u'常設', e_leader__exact=leader, e_status__exact=u'離職', e_grade__contains=u'師', e_lastdate__year=gs_year).exclude(e_id__contains='TMP', e_grade__contains=u'員').count()
            leave_prob = round((float(leave_num) / total_people) * 100, 2)
            if leave_prob > leave_prob_max_department:
                leave_prob_max_department = leave_prob

            # 國內出差
            cn_num = ETRAVELCOUNT.objects.filter(t_leader__exact=leader, t_type__exact='國內出差申請',
                                                 t_datetime__gt=(datetime.datetime.now() - relativedelta(months=7)),
                                                 t_datetime__lte=(datetime.datetime.now() - relativedelta(
                                                     months=1))).aggregate(travel_cn_out=Sum('t_count'))[
                'travel_cn_out']
            if not cn_num:
                cn_num = 0.00
            travel_cn = round(float(cn_num), 2)
            travel_cn_hc = round(travel_cn / total_people, 3)

            # 國外出差
            abroad_num = ETRAVELCOUNT.objects.filter(t_leader__exact=leader, t_type__exact='國外出差申請',
                                                     t_datetime__gt=(
                                                                 datetime.datetime.now() - relativedelta(months=7)),
                                                     t_datetime__lte=(datetime.datetime.now() - relativedelta(
                                                         months=1))).aggregate(travel_abroad_out=Sum('t_count'))[
                'travel_abroad_out']
            if not abroad_num:
                abroad_num = 0.00
            travel_abroad = round(float(abroad_num), 2)
            travel_abroad_hc = round(travel_abroad / total_people, 3)

            # 金石專案
            gs_num = EGSPBYLEADER.objects.filter(e_leader__exact=leader, e_year__exact=gs_year).aggregate(gs_out=Sum('e_closed_num'))['gs_out']
            target_num = EGSPBYLEADER.objects.filter(e_leader__exact=leader, e_year__exact=gs_year).aggregate(gs_target_out=Sum('e_team_target'))['gs_target_out']
            if gs_num and gs_num > 0:
                if target_num == 0:
                    gs_rate = 0.00
                else:
                    gs_rate = round((float(gs_num) / float(target_num)) * 100.0, 2)
            else:
                gs_num = 0
                gs_rate = 0.0

            # 義務時長
            duty_work = \
            EDutywork.objects.filter(d_leader__exact=leader, d_datetime__lt=datetime.datetime.now()).order_by(
                "-d_datetime")[0:6].aggregate(
                duty_work_sum=Sum(F('d_number') * F('d_population'), output_field=FloatField()))[
                'duty_work_sum']
            if not duty_work:
                duty_work = 0.00
            duty_work = round(float(duty_work) / 6, 2)
            duty_work_hc = round(duty_work / total_people, 3)

            # 超時10.5
            over_10_5_time = \
            EGreaterthan.objects.filter(g_leader__exact=leader, g_datetime__lt=datetime.datetime.now()).order_by(
                "-g_datetime")[0:6].aggregate(Sum('g_10_5_hours'))['g_10_5_hours__sum']
            if not over_10_5_time:
                over_10_5_time = 0.00
            over_10_5_time = round(float(over_10_5_time) / 6, 2)
            over_10_5_time_hc = round(over_10_5_time / total_people, 3)

            # 夜班天數
            night_work = round(float(sum(map(lambda x: x['sum_out'],
                                             EAttendance.objects.filter(a_leader__exact=leader).values(
                                                 'a_datetime').annotate(
                                                 sum_out=Sum('a_nightnum')).order_by('-a_datetime').order_by(
                                                 '-a_datetime')[0:6]))) / 6, 2)
            night_work_hc = round(night_work / total_people, 3)

            # 專利提案
            team_list = map(lambda x: x['t_team'], ETeam.objects.filter(t_leader__exact=leader).values('t_team'))
            patent = 0.0
            tax = 0.0
            task_force = 0.0
            idl = 0.0
            gold = 0.0
            ee = 0.0
            for team in team_list:
                if team == 'Inventory':
                    continue
                people = EEmployee.objects.filter(e_category__exact=u'常設', e_functionteam__exact=team, e_status__exact=u'在職', e_grade__contains=u'師').exclude(e_id__contains='TMP', e_grade__contains=u'員').count()
                patent_obj = E_MANUAL_BOMUS.objects.filter(m_team__exact=team, ).values("m_patent_proposal", "m_patent_closure", "m_tax_deduction", "m_task_force", "m_idl", "m_gold")
                patent += float(patent_obj[0]["m_patent_proposal"]) + (5 * float(patent_obj[0]["m_patent_closure"]))
                task_force += float(patent_obj[0]["m_task_force"])
                tax += float(patent_obj[0]["m_tax_deduction"])
                idl += float(patent_obj[0]["m_idl"])
                gold += float(patent_obj[0]["m_gold"])
                ee += float(patent_obj[0]["m_gold"]) * float(people)
            patent_target = float(total_people) / 3.0
            patent_rate = round((patent / patent_target) * 100, 2)
            # department 特有數據
            department_data_obj = EBONUSDEPARTMENT.objects.filter(bd_leader__exact=leader).values("bd_hr","bd_totalmoney","bd_violation","bd_belowquality")
            hr = department_data_obj[0]["bd_hr"]
            last_year_money = department_data_obj[0]["bd_totalmoney"]
            violation = department_data_obj[0]["bd_violation"]
            belowquality = department_data_obj[0]["bd_belowquality"]

            bonus_list_by_leader.append(
                {"belowquality":belowquality,"violation":violation,"last_year_money":last_year_money, "hr": hr,"ee":ee,"gold": gold, "idl": idl, "task_force": task_force, "tax": tax, "patent_rate": patent_rate,
                 "patent": patent, "travel_cn_hc": travel_cn_hc, "travel_abroad_hc": travel_abroad_hc,
                 "night_work_hc": night_work_hc, "over_10_5_time_hc": over_10_5_time_hc,
                 "duty_work_hc": duty_work_hc, "gs_rate": gs_rate, "team_id": team_id,
                 "night_work": night_work, 'leader': leader, 'travel_cn': travel_cn,
                 "travel_abroad": travel_abroad, "gsp_num": gs_num, "duty_work": duty_work,
                 "over_10_5_time": over_10_5_time, "leave_prob": leave_prob, "total_people": total_people})


    department_data_obj = EBONUSDEPARTMENT.objects.filter(bd_leader__exact='Shirley').values("bd_hr",
                                                                                          "bd_totalmoney",
                                                                                          "bd_violation",
                                                                                          "bd_belowquality")
    hr = department_data_obj[0]["bd_hr"]
    last_year_money = department_data_obj[0]["bd_totalmoney"]
    violation = department_data_obj[0]["bd_violation"]
    belowquality = department_data_obj[0]["bd_belowquality"]
    bonus_list_by_leader.append(
        {"belowquality": belowquality, "violation": violation, "last_year_money": last_year_money, "hr": hr, "ee": 0,
         "gold": 0, "idl": 0, "task_force": 0, "tax": 0, "patent_rate": 0,
         "patent": 0, "travel_cn_hc": 0, "travel_abroad_hc": 0,
         "night_work_hc": 0, "over_10_5_time_hc": 0,
         "duty_work_hc": 0, "gs_rate": 0, "team_id": team_id + 1,
         "night_work": 0, 'leader': 'Shirley', 'travel_cn': 0,
         "travel_abroad": 0, "gsp_num": 0, "duty_work": 0,
         "over_10_5_time": 0, "leave_prob": 0, "total_people": 11})
    team_id += 2







    for leader in leader_list:
        team_list = map(lambda x:x['t_team'], ETeam.objects.filter(t_leader__exact=leader).values('t_team'))
        for team in team_list:
            team_leader = ETeam.objects.filter(t_team__exact=team).values("t_subject_leader")[0]["t_subject_leader"]

            team_id += 1

            # 離職率
            total_people = EEmployee.objects.filter(e_category__exact=u'常設', e_leader__exact=leader,
                                                    e_functionteam__exact=team, e_status__exact=u'在職',
                                                    e_grade__contains=u'師').exclude(e_id__contains='TMP',
                                                                                    e_grade__contains=u'員').count()
            if total_people == 0:
                continue
            leave_num = EEmployee.objects.filter(e_category__exact=u'常設', e_leader__exact=leader,
                                                 e_functionteam__exact=team, e_status__exact=u'離職',
                                                 e_grade__contains=u'師', e_lastdate__year=gs_year).exclude(
                e_id__contains='TMP',
                e_grade__contains=u'員').count()

            leave_prob = round((float(leave_num) / total_people) * 100, 2)
            if leave_prob > leave_prob_max:
                leave_prob_max = leave_prob

            # 國內出差
            cn_num = ETRAVELCOUNT.objects.filter(t_functionteam__exact=team, t_type__exact='國內出差申請',t_datetime__gt=(datetime.datetime.now()-relativedelta(months=7)),t_datetime__lte=(datetime.datetime.now()-relativedelta(months=1))).aggregate(travel_cn_out = Sum('t_count'))['travel_cn_out']
            if not cn_num:
                cn_num = 0.00
            travel_cn = round(float(cn_num), 2)
            travel_cn_hc = round(travel_cn/total_people, 3)

            #國外出差
            abroad_num = ETRAVELCOUNT.objects.filter(t_functionteam__exact=team, t_type__exact='國外出差申請',t_datetime__gt=(datetime.datetime.now()-relativedelta(months=7)),t_datetime__lte=(datetime.datetime.now()-relativedelta(months=1))).aggregate(travel_abroad_out = Sum('t_count'))['travel_abroad_out']
            if not abroad_num:
                abroad_num = 0.00
            travel_abroad = round(float(abroad_num), 2)
            travel_abroad_hc = round(travel_abroad/total_people, 3)

            #金石專案
            gs_obj = EGSPBYLEADER.objects.filter(e_functionteam__exact=team, e_year__exact=gs_year)
            if gs_obj:
                gs_num = gs_obj.values('e_closed_num')[0]['e_closed_num']
                target_num = gs_obj.values('e_team_target')[0]['e_team_target']
                if target_num == 0:
                    gs_rate = 0.00
                else:
                    gs_rate = round((float(gs_num) / float(target_num)) * 100.0, 2)
            else:
                gs_num = 0
                gs_rate = 0.0


            #義務時長
            duty_work = ESectionDutywork.objects.filter(d_section__exact=team, d_datetime__lt=datetime.datetime.now()).order_by(
                    "-d_datetime")[0:6].aggregate(
                    duty_work_sum=Sum(F('d_number') * F('d_population'), output_field=FloatField()))[
                    'duty_work_sum']
            if not duty_work:
                duty_work = 0.00
            duty_work = round(float(duty_work) / 6, 2)
            duty_work_hc = round(duty_work/total_people,3)

            # 超時10.5
            over_10_5_time =  ESectionGreaterthan.objects.filter(g_section__exact=team, g_datetime__lt=datetime.datetime.now()).order_by(
                    "-g_datetime")[0:6].aggregate(Sum('g_10_5_hours'))['g_10_5_hours__sum']
            if not over_10_5_time:
                over_10_5_time = 0.00
            over_10_5_time = round(float(over_10_5_time) / 6, 2)
            over_10_5_time_hc = round(over_10_5_time/total_people,3)

            # 夜班天數
            night_work = round(float(sum(map(lambda x: x['sum_out'],
            EAttendance.objects.filter(a_leader__exact=leader,a_team__exact=team).values('a_datetime').annotate(
                sum_out=Sum('a_nightnum')).order_by('-a_datetime').order_by('-a_datetime')[0:6])))/6, 2)
            night_work_hc = round(night_work/total_people,3)


            # 專利提案
            patent_obj = E_MANUAL_BOMUS.objects.filter(m_team__exact=team,).values("m_patent_proposal","m_patent_closure","m_tax_deduction","m_task_force","m_idl","m_gold")
            patent = float(patent_obj[0]["m_patent_proposal"]) + (5*float(patent_obj[0]["m_patent_closure"]))
            patent_target = math.ceil(gs_obj.values('e_team_hc')[0]['e_team_hc']/3.0)
            patent_rate = round(((float(patent_obj[0]["m_patent_proposal"]) + (float(patent_obj[0]["m_patent_closure"])))/patent_target)*100,3)

            #稅務抵扣
            tax = float(patent_obj[0]["m_tax_deduction"])

            # task force
            task_force = float(patent_obj[0]["m_task_force"])

            # idl
            idl = float(patent_obj[0]["m_idl"])

            # gold
            gold = float(patent_obj[0]["m_gold"])
            ee = gold * float(total_people)

            bonus_list.append({"ee":ee,"gold":gold,"idl":idl,"task_force":task_force,"tax":tax,"patent_rate":patent_rate,"patent":patent,"travel_cn_hc":travel_cn_hc,"travel_abroad_hc":travel_abroad_hc,"night_work_hc":night_work_hc, "over_10_5_time_hc":over_10_5_time_hc,"duty_work_hc":duty_work_hc,"gs_rate":gs_rate, "team_leader": team_leader, "team_id": team_id, "night_work": night_work,'leader': leader, 'team': team, 'travel_cn': travel_cn, "travel_abroad": travel_abroad, "gsp_num": gs_num, "duty_work": duty_work, "over_10_5_time": over_10_5_time,"leave_prob": leave_prob, "total_people": total_people})



    # for leader in leader_list:
    #     leave_num = Eleavenum.objects.filter(l_leader__exact=leader,l_datetime__gt=(datetime.datetime.now()-relativedelta(months=13)),l_datetime__lte=(datetime.datetime.now()-relativedelta(months=1))).aggregate(leave_num_out=Sum('l_leavenum'))['leave_num_out']
    #     if not leave_num:
    #         leave_num = 0.00
    #     total_people = EEmployee.objects.filter(e_category__exact=u'常設',e_leader__exact=leader, e_status__exact=u'在職',
    #                                                e_grade__contains=u'師').exclude(e_id__contains='TMP',
    #                                                                           e_grade__contains=u'員').count()
    #     leave_prob = round((float(leave_num)/total_people)*100, 2)
    #     if leave_prob > leave_prob_max:
    #         leave_prob_max = leave_prob
    #
    #     cn_num = ETRAVELCOUNT.objects.filter(t_leader__exact=leader, t_type__exact='國內出差申請',t_datetime__gt=(datetime.datetime.now()-relativedelta(months=7)),t_datetime__lte=(datetime.datetime.now()-relativedelta(months=1))).aggregate(travel_cn_out = Sum('t_count'))['travel_cn_out']
    #     if cn_num:
    #         travel_cn = round(float(cn_num)/6, 2)
    #     else:
    #         travel_cn = 0.00
    #     total_travel_cn += travel_cn
    #
    #     abroad_num = ETRAVELCOUNT.objects.filter(t_leader__exact=leader, t_type__exact='國外出差申請',t_datetime__gt=(datetime.datetime.now()-relativedelta(months=7)),t_datetime__lte=(datetime.datetime.now()-relativedelta(months=1))).aggregate(travel_abroad_out = Sum('t_count'))['travel_abroad_out']
    #     if abroad_num:
    #         travel_abroad = round(float(abroad_num)/6, 2)
    #     else:
    #         travel_abroad = 0.00
    #     total_travel_abroad += travel_abroad
    #
    #     night_work = map(lambda x: x['sum_out'],
    #         EAttendance.objects.filter(a_leader__exact=leader).values('a_datetime').annotate(
    #             sum_out=Sum('a_nightnum')).order_by('-a_datetime').order_by('-a_datetime')[0:6])
    #
    #     night_work = round(float(sum(night_work))/6, 2)
    #     total_night_work += night_work
    #
    #
    #     gs_num = EGSPBYLEADER.objects.filter(e_leader__exact=leader, e_year__exact=gs_year).aggregate(gs_sum=Sum('e_gsp_num'))['gs_sum']
    #     if not gs_num:
    #         gs_num = 0.00
    #     total_gs_num += gs_num
    #
    #     over_10_5_time = round(float(ETimeout.objects.filter(t_leader__exact=leader, t_datetime__lt=datetime.datetime.now()).order_by("-t_datetime")[0:6].aggregate(Sum('t_over105'))['t_over105__sum'])/6, 2)
    #     total_over_10_5 += over_10_5_time
    #
    #     duty_work = round(EDutywork.objects.filter(d_leader__exact=leader,d_datetime__lt= datetime.datetime.now()).order_by("-d_datetime")[0:6].aggregate(duty_work_sum = Sum(F('d_number')*F('d_population'),output_field=FloatField()))['duty_work_sum']/6, 2)
    #     total_duty_work += duty_work
    #
    #     bonus_list.append({'leader': leader,"gsp_num":gs_num,"duty_work":duty_work,"over_10_5_time": over_10_5_time,"night_work":night_work,'travel_cn':travel_cn,"travel_abroad":travel_abroad,"leave_prob":leave_prob,"total_people":total_people})


    bonus_list.append(
        {"ee": 0, "gold": 0, "idl": 0, "task_force": 0, "tax": 0, "patent_rate": 0,
         "patent": 0, "travel_cn_hc": 0, "travel_abroad_hc": 0,
         "night_work_hc": 0, "over_10_5_time_hc": 0, "duty_work_hc": 0,
         "gs_rate": 0, "team_leader": u'Shirley', "team_id": team_id + 1, "night_work": 0, 'leader': u'Shirley',
         'team': "ES", 'travel_cn': 0, "travel_abroad": 0, "gsp_num": 0,
         "duty_work": 0, "over_10_5_time": 0, "leave_prob": 0,
         "total_people": 11})

    leave_point_total = 0.00
    for bonus in bonus_list_by_leader:
        bonus["leave_prob_point"] = round((((leave_prob_max_department - bonus["leave_prob"])/100) *  bonus["total_people"]), 2)
    for bonus in bonus_list:
        bonus["leave_prob_point"] = round((((leave_prob_max - bonus["leave_prob"])/100) *  bonus["total_people"]), 2)
        # leave_point_total += bonus["leave_prob_point"]
    # 获取 右上角 金钱数值
    bp_money = {}
    bp_obj = EBONUSPERCENTAGE.objects.filter().order_by("-edit_time")[0]
    bp_money['bp_totalmoney'] = bp_obj.bp_totalmoney
    bp_money['bp_personalmoney'] = bp_obj.bp_personalmoney
    bp_money['bp_teammoney'] = bp_obj.bp_teammoney
    bp_money['bp_othermoney'] = bp_obj.bp_othermoney
    bp_per = {}

    bp_per["bp_otherper_t"] = bp_obj.bp_otherper_t
    bp_per["bp_otherper_d"] = bp_obj.bp_otherper_d
    bp_per["bp_taskforceper_t"] = bp_obj.bp_taskforceper_t
    bp_per["bp_taskforceper_d"] = bp_obj.bp_taskforceper_d
    bp_per["bp_hrper_d"] = bp_obj.bp_hrper_d
    bp_per["bp_proposal_t"] = bp_obj.bp_proposal_t
    bp_per["bp_proposal_d"] = bp_obj.bp_proposal_d
    bp_per["bp_ee_t"] = bp_obj.bp_ee_t
    bp_per["bp_ee_d"] = bp_obj.bp_ee_d
    bp_per["bp_idl_t"] = bp_obj.bp_idl_t
    bp_per["bp_idl_d"] = bp_obj.bp_idl_d
    bp_per["bp_duty_t"] = bp_obj.bp_duty_t
    bp_per["bp_duty_d"] = bp_obj.bp_duty_d
    bp_per["bp_10_5_t"] = bp_obj.bp_10_5_t
    bp_per["bp_10_5_d"] = bp_obj.bp_10_5_d
    bp_per["bp_night_t"] = bp_obj.bp_night_t
    bp_per["bp_night_d"] = bp_obj.bp_night_d
    bp_per["bp_travel_abroad_t"] = bp_obj.bp_travel_abroad_t
    bp_per["bp_travel_abroad_d"] = bp_obj.bp_travel_abroad_d
    bp_per["bp_travel_cn_t"] = bp_obj.bp_travel_cn_t
    bp_per["bp_travel_cn_d"] = bp_obj.bp_travel_cn_d
    bp_per["bp_leave_t"] = bp_obj.bp_leave_t
    bp_per["bp_leave_d"] = bp_obj.bp_leave_d

    bp_per["bp_gsweight_t"] = bp_obj.bp_gsweight_t
    bp_per["bp_gsweight_d"] = bp_obj.bp_gsweight_d
    bp_per["bp_patentweight_t"] = bp_obj.bp_patentweight_t
    bp_per["bp_patentweight_d"] = bp_obj.bp_patentweight_d
    bp_per["bp_taxweight_t"] = bp_obj.bp_taxweight_t
    bp_per["bp_taxweight_d"] = bp_obj.bp_taxweight_d


    return render_to_response('NPI_EERF/table_score.html', {'bp_per':bp_per,'bonus_list_by_leader':bonus_list_by_leader, 'user_mode':user_mode,'bonus_list': bonus_list, 'user_cname': user_cname,'total_gs_num':total_gs_num, 'total_duty_work':total_duty_work,"total_over_10_5": total_over_10_5,"total_night_work":total_night_work,"total_travel_cn":total_travel_cn,"total_travel_abroad":total_travel_abroad,"total_leave_prob":total_leave_prob,"leave_point_total":leave_point_total, 'bp_money':bp_money})


    # if req.POST:
    #     mode = req.POST.get('selected_mode')
    #     if mode == '新增':
    #         pass
    #     elif mode == '读取':
    #         record_id = req.POST.get('selected_record')
    #         pass






@csrf_exempt
def report_message_third(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    月人力超时状态表格的数据，根据用户选择的时间、leader、team展示对应的 上个月数据。
    用户选择的日期 在每个月的 1-5号时，显示的是 上上个月的数据，大于5号时显示的是上个月数据
    :param req:
    :return:员工考勤数据
    """
    if req.POST:
        # 获取前台选定的查找时间
        get_html_time = req.POST.get('_time').split('-')
        search_year = int(get_html_time[0])
        search_day = int(get_html_time[2])
        search_month = int(get_html_time[1]) - 1 if search_day >= UPDATE_DATA_DATE else int(get_html_time[1]) - 2
        # 当跨年度时 年份要减一，月份加12，-1 指的是1月1号-5号这段时间，0指的是1月5号-31号
        if search_month < 1:
            search_year = search_year - 1
            search_month = search_month + 12

        search_year_month = str(search_year) + "-" + str(search_month)
        # 获取前台选定的leader/ team
        leader = req.POST.get('selectedLeader')
        team = req.POST.get('selectedTeam')
        # 员工考勤所有数据
        all_atte_data = []
        worktime_list = []
        if leader == 'All':
            eattendance_obj = EAttendance.objects.filter(a_datetime__year=search_year,
                                                         a_datetime__month=search_month).order_by("-a_avgoverhours")
            print(eattendance_obj.count())
            all_atte_data = list(eattendance_obj.values())
            for i in all_atte_data:
                a_employee = i['a_employee']
                try:
                    epersonalworktime_obj = EPersonalWorkTime.objects.get(p_employee=a_employee,
                                                                            p_datetime__year=search_year,
                                                                            p_datetime__month=search_month)
                except Exception as e:
                    # 主要滤掉处长
                    continue

                i['p_10_5_hours'] = epersonalworktime_obj.p_10_5_hours
                i['p_11_5_hours'] = epersonalworktime_obj.p_11_5_hours
                i['p_12_5_hours'] = epersonalworktime_obj.p_12_5_hours
                i['a_interval'] = search_year_month
                worktime_list.append(i)
        else:
            if team == 'All':
                eattendance_obj = EAttendance.objects.filter(a_datetime__year=search_year,
                                                             a_datetime__month=search_month,
                                                             a_leader__exact=leader).order_by("-a_avgoverhours")
                all_atte_data = list(eattendance_obj.values())
                for i in all_atte_data:
                    a_employee = i['a_employee']
                    try:
                        epersonalworktime_obj = EPersonalWorkTime.objects.get(p_employee=a_employee,
                                                                              p_datetime__year=search_year,
                                                                              p_datetime__month=search_month)
                    except Exception as e:
                        # 主要滤掉处长
                        continue

                    i['p_10_5_hours'] = epersonalworktime_obj.p_10_5_hours
                    i['p_11_5_hours'] = epersonalworktime_obj.p_11_5_hours
                    i['p_12_5_hours'] = epersonalworktime_obj.p_12_5_hours
                    i['a_interval'] = search_year_month
                    worktime_list.append(i)
            else:
                emp_data = EEmployee.objects.all()
                the_team_emp = []
                for ee in emp_data:
                    if ee.e_functionteam == team:
                        the_team_emp.append(ee.e_id)
                eattendance_obj = EAttendance.objects.filter(a_datetime__year=search_year,
                                                             a_datetime__month=search_month,
                                                             a_leader__exact=leader,
                                                             a_employee__in=the_team_emp).order_by("-a_avgoverhours")
                all_atte_data = list(eattendance_obj.values())
                for i in all_atte_data:
                    a_employee = i['a_employee']
                    try:
                        epersonalworktime_obj = EPersonalWorkTime.objects.get(p_employee=a_employee,
                                                                              p_datetime__year=search_year,
                                                                              p_datetime__month=search_month)
                    except Exception as e:
                        # 主要滤掉处长
                        continue

                    i['p_10_5_hours'] = epersonalworktime_obj.p_10_5_hours
                    i['p_11_5_hours'] = epersonalworktime_obj.p_11_5_hours
                    i['p_12_5_hours'] = epersonalworktime_obj.p_12_5_hours
                    i['a_interval'] = search_year_month
                    worktime_list.append(i)

        return HttpResponse(json.dumps(worktime_list, cls=DjangoJSONEncoder, ensure_ascii=False))


@csrf_exempt
def report_message_four(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    人力实时超时状态表格的数据，根据用户选择的时间、leader、team展示对应的 上个月数据。
    用户选择的日期 在每个月的 1-5号时，显示的是 上上个月的数据，大于5号时显示的是上个月数据
    :param req:
    :return:员工考勤数据
    """
    if req.POST:
        # 获取前台选定的查找时间
        get_html_time = req.POST.get('_time').split('-')
        search_year = int(get_html_time[0])
        search_day = int(get_html_time[2])
        #search_month = int(get_html_time[1]) - 1 if search_day >= UPDATE_DATA_DATE else int(get_html_time[1]) - 2
        if search_day == 1:
            search_month = int(get_html_time[1]) - 1
        else:
            search_month = int(get_html_time[1])
        # 当跨年度时 年份要减一，月份加12，-1 指的是1月1号-5号这段时间，0指的是1月5号-31号
        if search_month < 1:
            search_year = search_year - 1
            search_month = search_month + 12

        # 获取前台选定的leader/ team
        leader = req.POST.get('selectedLeader')
        team = req.POST.get('selectedTeam')
        # 员工考勤所有数据
        all_atte_data = []
        lmfworktime_list = []
        if leader == 'All':
            eattendance_obj = ELMFAttendance.objects.filter(a_datetime__year=search_year,
                                                         a_datetime__month=search_month).order_by("-a_avgoverhours")
            all_atte_data = list(eattendance_obj.values())
            for i in all_atte_data:
                a_employee = i['a_employee']
                try:
                    elmfpersonalworktime_obj = ELMFPersonalWorkTime.objects.get(p_employee=a_employee,
                                                                                p_datetime__year=search_year,
                                                                            p_datetime__month=search_month)
                except Exception as e:
                    # 主要滤掉处长
                    continue

                i['p_10_5_hours'] = elmfpersonalworktime_obj.p_10_5_hours
                i['p_11_5_hours'] = elmfpersonalworktime_obj.p_11_5_hours
                i['p_12_5_hours'] = elmfpersonalworktime_obj.p_12_5_hours
                lmfworktime_list.append(i)
        else:
            if team == 'All':
                eattendance_obj = ELMFAttendance.objects.filter(a_datetime__year=search_year,
                                                             a_datetime__month=search_month,
                                                             a_leader__exact=leader).order_by("-a_avgoverhours")
                all_atte_data = list(eattendance_obj.values())
                for i in all_atte_data:
                    a_employee = i['a_employee']
                    try:
                        elmfpersonalworktime_obj = ELMFPersonalWorkTime.objects.get(p_employee=a_employee,
                                                                                    p_datetime__year=search_year,
                                                                                    p_datetime__month=search_month)
                    except Exception as e:
                        # 主要滤掉处长
                        continue

                    i['p_10_5_hours'] = elmfpersonalworktime_obj.p_10_5_hours
                    i['p_11_5_hours'] = elmfpersonalworktime_obj.p_11_5_hours
                    i['p_12_5_hours'] = elmfpersonalworktime_obj.p_12_5_hours
                    lmfworktime_list.append(i)
            else:
                emp_data = EEmployee.objects.all()
                the_team_emp = []
                for ee in emp_data:
                    if ee.e_functionteam == team:
                        the_team_emp.append(ee.e_id)
                eattendance_obj = ELMFAttendance.objects.filter(a_datetime__year=search_year,
                                                             a_datetime__month=search_month,
                                                             a_leader__exact=leader,
                                                             a_employee__in=the_team_emp).order_by("-a_avgoverhours")
                all_atte_data = list(eattendance_obj.values())
                for i in all_atte_data:
                    a_employee = i['a_employee']
                    try:
                        elmfpersonalworktime_obj = ELMFPersonalWorkTime.objects.get(p_employee=a_employee,
                                                                                    p_datetime__year=search_year,
                                                                                    p_datetime__month=search_month)
                    except Exception as e:
                        # 主要滤掉处长
                        continue
                        
                    i['p_10_5_hours'] = elmfpersonalworktime_obj.p_10_5_hours
                    i['p_11_5_hours'] = elmfpersonalworktime_obj.p_11_5_hours
                    i['p_12_5_hours'] = elmfpersonalworktime_obj.p_12_5_hours
                    lmfworktime_list.append(i)

        return HttpResponse(json.dumps(lmfworktime_list, cls=DjangoJSONEncoder, ensure_ascii=False))


@csrf_exempt
def report_message_five(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    人力超时状态表格的数据，根据用户选择的时间、leader、team展示对应的 上个月数据。
    用户选择的日期 在每个月的 1-5号时，显示的是 上上个月的数据，大于5号时显示的是上个月数据
    :param req:
    :return:员工考勤数据
    """
    if req.POST:
        # 获取前台选定的查找时间 startTime endTime
        get_start_time = req.POST.get('startTime')
        get_end_time = req.POST.get('endTime')
        # 將开始时间和结束时间的 - 去除掉
        get_start_time = get_start_time.replace("-", "")
        get_end_time = get_end_time.replace("-", "")
        # 将字符串时间转化为 真正的时间格式
        new_start_time = datetime.datetime.strptime(get_start_time, '%Y%m%d')
        new_end_time = datetime.datetime.strptime(get_end_time, '%Y%m%d')
        # 获取 年周数 (2019, 7, 3)
        start_week_num = new_start_time.isocalendar()
        end_week_num = new_end_time.isocalendar()
        # 转换成 年 + 周
        start_week_value = int(str(start_week_num[0]) + str(start_week_num[1]))
        end_week_value = int(str(end_week_num[0]) + str(end_week_num[1]))

        # 10点后下班 员工 所有数据
        all_atte_data = {}

        # 需要按照 l_weeknum 排序
        lmf_obj = ELateMealFee.objects.filter(l_weeknum__gte=start_week_value, l_weeknum__lte=end_week_value).order_by("l_employee", "l_weeknum")
        # l_interval 'Name', 'Leader'
        interval_list = ['ID', 'Name', 'Leader']
        interval_weeknum_list = []
        # 遍历ELateMealFee的周间隔和年月 得到each_a ==> <type 'dict'>: {'l_weeknum': 201914, 'l_interval': u'2019.04.01~2019.04.07'}
        for each_a in lmf_obj.values("l_interval", "l_weeknum").distinct().order_by("l_interval"):
            # 把周间隔添加到间隔列表中
            interval_list.append(each_a["l_interval"])
            # 把年月 添加在年月份总列表中
            interval_weeknum_list.append(each_a["l_weeknum"])
        # 周间隔和年月所有数据汇入字典
        all_atte_data['table_name'] = interval_list
        all_atte_data['table_weeknum'] = interval_weeknum_list

        employee_interval_dict = {}  # {工号: [月份時段], .... }
        # 遍历数据库值 "l_employee", "l_interval"
        for each_a in lmf_obj.values("l_employee", "l_interval").distinct():
            # 判断工号是否在 employee_interval_dict字典中
            if each_a["l_employee"] not in employee_interval_dict.keys():
                # 不在 新增 key: [值,...]
                employee_interval_dict[each_a["l_employee"]] = [each_a["l_interval"]]
            else:
                # 在的话在对应的工号key后面添加 月份時段
                employee_interval_dict[each_a["l_employee"]].append(each_a["l_interval"])

        import copy  # 深拷贝,为了拷贝后不受影响
        # 8点后下班 员工 所有数据
        all_atte_data8 = copy.deepcopy(all_atte_data)
        # 9点后下班 员工 所有数据
        all_atte_data9 = copy.deepcopy(all_atte_data)
        # 11点后下班 员工 所有数据
        all_atte_data11 = copy.deepcopy(all_atte_data)


        # 遍历  选择的时间内的对象
        for each_list in lmf_obj:
            # 判断工号是否在 all_atte_data字典键中
            if each_list.l_employee not in all_atte_data.keys():
                # 不存在新增 <type 'list'>: [u'13625', '員工姓名', '主管', 當周十點后天數]
                all_atte_data[each_list.l_employee] = [each_list.l_employee, each_list.l_cname, each_list.l_leader, each_list.l_tenlate]
                # 不存在新增 <type 'list'>: [u'13625', '員工姓名', '主管', 當周8點后天數]
                all_atte_data8[each_list.l_employee] = [each_list.l_employee, each_list.l_cname, each_list.l_leader, each_list.l_eightlate]
                # 不存在新增 <type 'list'>: [u'13625', '員工姓名', '主管', 當周9點后天數]
                all_atte_data9[each_list.l_employee] = [each_list.l_employee, each_list.l_cname, each_list.l_leader, each_list.l_ninelate]
                # 不存在新增 <type 'list'>: [u'13625', '員工姓名', '主管', 當周11點后天數]
                all_atte_data11[each_list.l_employee] = [each_list.l_employee, each_list.l_cname, each_list.l_leader, each_list.l_elevenlate]
            else:
                # 在的话在对应的工号key后面添加 當周十點后天數
                all_atte_data[each_list.l_employee].append(each_list.l_tenlate)
                # 在的话在对应的工号key后面添加 當周8點后天數
                all_atte_data8[each_list.l_employee].append(each_list.l_eightlate)
                # 在的话在对应的工号key后面添加 當周9點后天數
                all_atte_data9[each_list.l_employee].append(each_list.l_ninelate)
                # 在的话在对应的工号key后面添加 當周11點后天數
                all_atte_data11[each_list.l_employee].append(each_list.l_elevenlate)
            # all_atte_data = list(eattendance_obj.values())

        # 8点,9点,10点,11点列表
        all_list = [all_atte_data, all_atte_data8, all_atte_data9, all_atte_data11]
        # 遍历
        for i in all_list:
            # 遍历员工 所有数据的 key
            for each_man in i.keys():
                if each_man != "table_name" and each_man != "table_weeknum":
                    # 取出所有 周间隔 列表
                    total_interval_list = i['table_name'][3:]
                    # 周间隔 列表 赋值给新的变量
                    this_employee_interval_list = employee_interval_dict[each_man]
                    # 相同判断
                    if this_employee_interval_list != total_interval_list:
                        # 遍历 total_interval_list周间隔 列表
                        for each_interval in total_interval_list:
                            # 判断是那个值不在
                            if each_interval not in this_employee_interval_list:
                                # 不存在则添加
                                this_employee_list = i[each_man]
                                #  插入到列表中的指定位置
                                this_employee_list.insert(total_interval_list.index(each_interval) + 3, 0)

            # 除去全是 0 的数据
            for each_v in i.keys():
                if each_v != "table_name" and each_v != "table_weeknum":
                    # 周间隔内判断超时加班个数  除去全为0的
                    if set(i[each_v][3:]) == {0}:
                        # pop删除
                        i.pop(each_v)

        return HttpResponse(json.dumps(all_list, cls=DjangoJSONEncoder, ensure_ascii=False))



def get_everymonth_num():
    """
    :Author: F1233225
    :Date: 2019-01-09
    获取每个leader每个月的人数(只统计 常设、师级人数) 用来计算 每个月人均...
    :return:
    """
    ee = EEmployee.objects.filter(e_category__exact=u'常設', e_grade__contains=u'師')
    leaders = get_leader()
    # 日期列表
    eg = EGreaterthan.objects.all().order_by('g_datetime')
    _list = [g.g_datetime for g in eg]
    seen = set()
    date_list = [x for x in _list if x not in seen and not seen.add(x)]
    alldata = {}
    edw = EDutywork.objects.all()
    for leader in leaders:

        for _date in date_list:
            try:
                count = edw.get(d_leader__exact=leader, d_datetime__exact=_date).d_population
            except Exception as e:
                print e
            # 在这个日期之前入职的并且还在职的
            # this_ee = ee.filter(e_leader__exact=leader, e_firstdate__lte=_date, e_status__exact=u'在職')

            # 现在已经离职 但是当时这个日期没离职的人数
            # not_yet = ee.filter(e_leader__exact=leader, e_status__exact=u'離職', e_lastdate__lte=_date)

            # count = this_ee.count() + not_yet.count()
            # each_data['num'].append(count)
            if leader not in alldata.keys():
                alldata[leader] = [count]
            else:
                alldata[leader].append(count)
    return alldata


def get_section_everymonth_num():
    """
    :Author: F1237077
    :Date: 2019-07-09
    获取每个科级下每个月的人数(只统计 常设、师级人数) 用来计算 每个月人均...
    :return:
    """
    ee = EEmployee.objects.filter(e_category__exact=u'常設', e_grade__contains=u'師')
    sections = get_section()
    # 日期列表
    eg = ESectionGreaterthan.objects.all().order_by('g_datetime')
    _list = [g.g_datetime for g in eg]
    seen = set()
    date_list = [x for x in _list if x not in seen and not seen.add(x)]
    alldata = {}
    edw = ESectionDutywork.objects.all()
    for section in sections:

        for _date in date_list:
            try:
                count = edw.get(d_section__exact=section, d_datetime__exact=_date).d_population
            except Exception as e:
                print e
            # 在这个日期之前入职的并且还在职的
            # this_ee = ee.filter(e_section__exact=section, e_firstdate__lte=_date, e_status__exact=u'在職')

            # 现在已经离职 但是当时这个日期没离职的人数
            # not_yet = ee.filter(e_section__exact=section, e_status__exact=u'離職', e_lastdate__lte=_date)

            # count = this_ee.count() + not_yet.count()
            # each_data['num'].append(count)
            if section not in alldata.keys():
                alldata[section] = [count]
                # print section
            else:
                alldata[section].append(count)

    return alldata


def nightwork(req):
    """
    晚上加班不同时间段人数统计
    :param req:
    :return:leader 的超时加班数据
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        user_cname, user_authority = get_CnameAndAuthority(username)
        data = get_everymonth_num()
        # 获取大于某个点加班数据 - 部级数据
        greaterthan_data = EGreaterthan.objects.all().order_by("g_datetime")
        greth_leader_dic = {}
        percentageData = {}

        for greaterthan in greaterthan_data:
            this_db_datetime = str(greaterthan.g_datetime)
            this_db_leader = greaterthan.g_leader
            this_db_total = float(greaterthan.g_ontime) + float(greaterthan.g_overtime)
            this_db_all_than_list = [float(greaterthan.g_ontime), float(greaterthan.g_overtime),
                                     float(greaterthan.g_9_hours), float(greaterthan.g_9_5_hours),
                                     float(greaterthan.g_10_hours), float(greaterthan.g_10_5_hours),
                                     float(greaterthan.g_11_hours), float(greaterthan.g_11_5_hours),
                                     float(greaterthan.g_12_hours), float(greaterthan.g_12_5_hours)]
            this_percentage = []
            for _value in this_db_all_than_list:
                if _value and this_db_total:
                    this_percentage.append(round(_value * 100 / this_db_total, 2))
                else:
                    this_percentage.append(0)

            if this_db_leader not in greth_leader_dic.keys():
                greth_leader_dic[this_db_leader] = [[this_db_datetime, this_db_all_than_list]]
                percentageData[this_db_leader] = [[this_db_datetime, this_percentage]]
            else:
                this_key_value_list = [this_db_datetime, this_db_all_than_list]
                greth_leader_dic[this_db_leader].append(this_key_value_list)
                this_percentage_key = [this_db_datetime, this_percentage]
                percentageData[this_db_leader].append(this_percentage_key)

        # leaders
        AllLeaders = get_leader()

        avg_greth_leader_data = {}
        for leader in AllLeaders:
            each_leader_greth_data = {}
            each_leader_greth_data['leader'] = leader
            each_leader_greth_data['data'] = []
            for i, each_leader in enumerate(greth_leader_dic[leader]):
                _list = [float('%.2f' % (x / data[leader][i])) for x in each_leader[1]]
                if leader not in avg_greth_leader_data.keys():
                    avg_greth_leader_data[leader] = [[each_leader[0], _list]]
                else:
                    avg_value_list = [each_leader[0], _list]
                    avg_greth_leader_data[leader].append(avg_value_list)

        # *****************************************************************************
        data = get_section_everymonth_num()
        # 获取大于某个点加班数据 - 科级数据
        greaterthan_section_data = ESectionGreaterthan.objects.all().order_by("g_datetime")
        greth_section_dic = {}
        percentageData_section = {}
        for greaterthan in greaterthan_section_data:
            this_db_datetime = str(greaterthan.g_datetime)
            this_db_section = greaterthan.g_section
            this_db_total = float(greaterthan.g_ontime) + float(greaterthan.g_overtime)
            this_db_all_than_list = [float(greaterthan.g_ontime), float(greaterthan.g_overtime),
                                     float(greaterthan.g_9_hours), float(greaterthan.g_9_5_hours),
                                     float(greaterthan.g_10_hours), float(greaterthan.g_10_5_hours),
                                     float(greaterthan.g_11_hours), float(greaterthan.g_11_5_hours),
                                     float(greaterthan.g_12_hours), float(greaterthan.g_12_5_hours)]
            this_percentage = []
            for _value in this_db_all_than_list:
                if _value and this_db_total:
                    this_percentage.append(round(_value * 100 / this_db_total, 2))
                else:
                    this_percentage.append(0)

            if this_db_section not in greth_section_dic.keys():
                greth_section_dic[this_db_section] = [[this_db_datetime, this_db_all_than_list]]
                percentageData_section[this_db_section] = [[this_db_datetime, this_percentage]]
            else:
                this_key_value_list = [this_db_datetime, this_db_all_than_list]
                greth_section_dic[this_db_section].append(this_key_value_list)
                this_percentage_key = [this_db_datetime, this_percentage]
                percentageData_section[this_db_section].append(this_percentage_key)

        # section
        AllSections = get_section()
        avg_greth_section_data = {}
        for section in AllSections:
            each_section_greth_data = {}
            each_section_greth_data['section'] = section
            each_section_greth_data['data'] = []
            for i, each_section in enumerate(greth_section_dic[section]):
                _list = [float('%.2f' % (x / data[section][i])) for x in each_section[1]]
                if section not in avg_greth_section_data.keys():
                    avg_greth_section_data[section] = [[each_section[0], _list]]
                else:
                    avg_value_list = [each_section[0], _list]
                    avg_greth_section_data[section].append(avg_value_list)


        response = render_to_response('NPI_EERF/Nightwork.html',
                                      {'username': username, 'user_cname': user_cname, 'user_authority': user_authority,
                                       "greth_leader_dic": json.dumps(greth_leader_dic),
                                       "AllLeaders": json.dumps(AllLeaders),
                                       "percentageData": json.dumps(percentageData),
                                       'avg_greth_leader_data': json.dumps(avg_greth_leader_data),

                                       "greth_section_dic": json.dumps(greth_section_dic),
                                       "AllSections": json.dumps(AllSections),
                                       "percentageData_section": json.dumps(percentageData_section),
                                       'avg_greth_section_data': json.dumps(avg_greth_section_data)
                                       })
        return response
    else:
        return HttpResponseRedirect('/login/')


def eveningtrips(req):
    """
    夜班人数统计
    :param req:
    :return:leader的夜班人数
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        # 根据用户名 获取中文名及职级
        user_cname, user_authority = get_CnameAndAuthority(username)
        # 夜班人数 - 部级
        enightshift_data = ENightshift.objects.all().order_by("n_datetime")
        enightshift_leader_dic = {}
        for en in enightshift_data:
            # 生成該筆數據的日期
            this_db_datetime = str(en.n_datetime)
            # 部长名
            this_db_leader = en.n_leader
            # 晚班人次
            this_db_number = float(en.n_number)

            # 部级领导英文名 --> 写入字典  不存在新增,存在添加
            if this_db_leader not in enightshift_leader_dic.keys():
                enightshift_leader_dic[this_db_leader] = [[this_db_datetime, this_db_number]]
            else:
                this_key_value_list = [this_db_datetime, this_db_number]
                enightshift_leader_dic[this_db_leader].append(this_key_value_list)

        # 夜班人数 - 科级
        esectionnightshift_data = ESectionNightshift.objects.all().order_by("n_datetime")
        esectionnightshift_leader_dic = {}
        for en in esectionnightshift_data:
            # 生成該筆數據的日期
            this_db_datetime = str(en.n_datetime)
            # 科名
            this_db_section = en.n_section
            # 晚班人次
            this_db_number = float(en.n_number)

            # 科级英文名 --> 写入字典  不存在新增,存在添加
            if this_db_section not in esectionnightshift_leader_dic.keys():
                esectionnightshift_leader_dic[this_db_section] = [[this_db_datetime, this_db_number]]
            else:
                this_key_value_list = [this_db_datetime, this_db_number]
                esectionnightshift_leader_dic[this_db_section].append(this_key_value_list)

        # leaders
        AllLeaders = json.dumps(get_leader())

        response = render_to_response('NPI_EERF/Eveningtrips.html', {'username': username, 'user_cname': user_cname,
                                                                     'user_authority': user_authority,
                                                                     "enightshift_leader_dic": json.dumps(
                                                                         enightshift_leader_dic),
                                                                     "esectionnightshift_leader_dic": json.dumps(
                                                                         esectionnightshift_leader_dic),
                                                                     "AllLeaders": AllLeaders})
        return response
    else:
        return HttpResponseRedirect('/login/')


def report_download(request):
    """
    报表下载
    :param request:
    :return:
    """
    this_path = r'D:\OracleData\EERF\EISP'
    dir_list = os.listdir(this_path)
    newDir = get_new_dir(dir_list)
    date_dir_path = os.path.join(this_path, newDir)
    the_file_name = 'Dimission.xls'
    # 要下载的文件路径
    filename = date_dir_path + "/" + the_file_name
    if os.path.isfile(filename):
        response = StreamingHttpResponse(readfile(filename))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
        return response
    else:
        return HttpResponse("文件不存在！")


def readfile(filename, chunk_size=512):
    """
    读取文件
    :param filename:
    :param chunk_size:
    :return:
    """
    with open(filename, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


def get_new_dir(dir_list):
    """
    获取新的dir
    :param dir_list:
    :return:
    """
    n = len(dir_list)
    new_dir = dir_list[0]
    for r in range(n):
        if datetime.datetime.strptime(dir_list[r], "%Y-%m-%d-%H-%M-%S") \
                > datetime.datetime.strptime(new_dir, "%Y-%m-%d-%H-%M-%S"):
            new_dir = dir_list[r]
    return new_dir


@csrf_exempt
def report_message(req):
    """
    报表实时人力状态
    :param req:
    :return:
    """
    if req.POST:

        # 写在前面：redis 是在ram里面的一个数据库 ，本质上是数据库，当程序运行一次写操作，结束后redis并没有擦除这个key的信息，
        # 因此连续运行写入的程序的话
        # 例如lpush("key",111),lrange("key",0,-1)运行了一次之后继续运行一次代码，则redis 的key会记录两次111,
        # 因此有必要在这之前注释一部分写入的代码或者其它方案避免

        r = redis.StrictRedis(host="10.175.94.58", port=6379, db=1, password='123456', decode_responses=True)
        # print "POST"
        get_html_time = req.POST.get('_time')
        # print "get_html_time:", get_html_time
        # 获取当天时间
        today_time = datetime.datetime.now()
        # 当天时间早上7点
        seven_time = datetime.datetime.strptime(str(today_time).replace(str(today_time)[str(today_time).index(":")-2:], "07:00:00"), '%Y-%m-%d %H:%M:%S')
        # 创建一个key为dict的字典
        group_dir = collections.defaultdict(dict)
        # 判断当前时间是否大于7点
        if today_time > seven_time:
            # 判断redis数据库是否存在 get_html_time的时间
            if r.hgetall(get_html_time):
                # 存在直接访问redis
                # String
                # print("----------string---------------")
                group_dir['EERF Total'] = eval(r.hget(get_html_time, 'EERF Total'))
                group_dir['Magma'] = eval(r.hget(get_html_time, 'Magma'))
                group_dir['default_factory'] = {}
                group_dir['Group1'] = eval(r.hget(get_html_time, 'Group1'))
                group_dir['Group2'] = eval(r.hget(get_html_time, 'Group2'))
                group_dir['Group3'] = eval(r.hget(get_html_time, 'Group3'))
            else:
                # 获取查找的时间
                sreach_time = datetime.datetime.strptime(get_html_time, '%Y-%m-%d')
                sreach_time_start = datetime.datetime.strptime('%d/01/01' % sreach_time.year, '%Y/%m/%d')
                sreach_time_end = datetime.datetime.strptime('%d/12/31' % sreach_time.year, '%Y/%m/%d')

                all_group_data = ELeader.objects.all()
                leadernum_foc_dic = {}

                for g_row in all_group_data:
                    leader_ename = EEmployee.objects.get(e_id__iexact=g_row.edepartment.d_leadernum).e_ename
                    fonction_list = [f_t.t_team for f_t in g_row.eteam_set.all()]
                    if not fonction_list:
                        continue
                    elif g_row.edepartment.d_leadernum in leadernum_foc_dic.keys():
                        fonction_list.extend(leadernum_foc_dic[g_row.edepartment.d_leadernum])
                    leadernum_foc_dic[g_row.edepartment.d_leadernum] = fonction_list
                    # 初始化function数据
                    foc_data_dic = {}
                    leader_EngGL_all = 0
                    leader_EngZZ_all = 0
                    leader_EngTG_all = 0
                    leader_TechGL_all = 0
                    leader_TechZZ_all = 0
                    demand_all = 0
                    recruiting_all = 0
                    employment_all = 0
                    surplus_all = 0
                    for f_row in fonction_list:
                        if f_row == 'Inventory':
                            continue
                        row_data_list = []
                        # 中干（GL）在职
                        ZG_GL_On = EEmployee.objects.filter(e_status__exact=u'在職', e_category__exact=u'常設',
                                                            e_difference__contains=u'中',
                                                            e_grade__contains=u'師', e_place__exact='GL',
                                                            e_leader__exact=leader_ename,
                                                            e_functionteam__exact=f_row)
                        # 中干（GL）离职
                        ZG_GL_Off = EEmployee.objects.filter(e_status__exact=u'離職', e_category__exact=u'常設',
                                                             e_difference__contains=u'中',
                                                             e_grade__contains=u'師', e_place__exact='GL',
                                                             e_leader__exact=leader_ename,
                                                             e_functionteam__exact=f_row, e_lastdate__gt=sreach_time)
                        ZG_GL = ZG_GL_On.count() + ZG_GL_Off.count()
                        leader_EngGL_all += ZG_GL
                        row_data_list.append(ZG_GL)
                        row_data_list.append(leader_EngGL_all)

                        # 中干（ZZ）在职
                        ZG_ZZ_On = EEmployee.objects.filter(e_status__exact=u'在職', e_category__exact=u'常設',
                                                            e_difference__contains=u'中',
                                                            e_grade__contains=u'師', e_place__exact='ZZ',
                                                            e_leader__exact=leader_ename,
                                                            e_functionteam__exact=f_row)
                        # 中干（ZZ）离职
                        ZG_ZZ_Off = EEmployee.objects.filter(e_status__exact=u'離職', e_category__exact=u'常設',
                                                             e_difference__contains=u'中',
                                                             e_grade__contains=u'師', e_place__exact='ZZ',
                                                             e_leader__exact=leader_ename,
                                                             e_functionteam__exact=f_row, e_lastdate__gt=sreach_time)
                        ZG_ZZ = ZG_ZZ_On.count() + ZG_ZZ_Off.count()
                        leader_EngZZ_all += ZG_ZZ
                        row_data_list.append(ZG_ZZ)
                        row_data_list.append(leader_EngZZ_all)

                        # 台干 在职
                        TG_On = EEmployee.objects.filter(e_status__exact=u'在職', e_category__exact=u'常設',
                                                         e_difference__contains=u'臺',
                                                         e_grade__contains=u'師', e_leader__exact=leader_ename,
                                                         e_functionteam__exact=f_row)
                        # 台干 离职
                        TGOff = EEmployee.objects.filter(e_status__exact=u'離職', e_category__exact=u'常設',
                                                         e_difference__contains=u'臺',
                                                         e_grade__contains=u'師', e_leader__exact=leader_ename,
                                                         e_functionteam__exact=f_row, e_lastdate__gt=sreach_time)
                        TG = TG_On.count() + TGOff.count()
                        leader_EngTG_all += TG
                        row_data_list.append(TG)
                        row_data_list.append(leader_EngTG_all)

                        # 员级（GL） 在职
                        TechGL_On = EEmployee.objects.filter(e_status__exact=u'在職', e_category__exact=u'常設',
                                                             e_place__exact='GL',
                                                             e_grade__contains=u'員', e_leader__exact=leader_ename,
                                                             e_functionteam__exact=f_row)
                        # 员级（GL） 离职
                        TechGL_Off = EEmployee.objects.filter(e_status__exact=u'離職', e_category__exact=u'常設',
                                                              e_place__exact='GL',
                                                              e_grade__contains=u'員', e_leader__exact=leader_ename,
                                                              e_functionteam__exact=f_row, e_lastdate__gt=sreach_time)
                        TechGL = TechGL_On.count() + TechGL_Off.count()
                        leader_TechGL_all += TechGL
                        row_data_list.append(TechGL)
                        row_data_list.append(leader_TechGL_all)

                        # 员级（ZZ）
                        TechZZ_On = EEmployee.objects.filter(e_status__exact=u'在職', e_category__exact=u'常設',
                                                             e_place__exact='ZZ',
                                                             e_grade__contains=u'員', e_leader__exact=leader_ename,
                                                             e_functionteam__exact=f_row)
                        TechZZ_Off = EEmployee.objects.filter(e_status__exact=u'離職', e_category__exact=u'常設',
                                                              e_place__exact='ZZ',
                                                              e_grade__contains=u'員', e_leader__exact=leader_ename,
                                                              e_functionteam__exact=f_row, e_lastdate__gt=sreach_time)
                        TechZZ = TechZZ_On.count() + TechZZ_Off.count()
                        leader_TechZZ_all += TechZZ
                        row_data_list.append(TechZZ)
                        row_data_list.append(leader_TechZZ_all)

                        # 总师级人数
                        Eng_all = ZG_GL + ZG_ZZ + TG
                        row_data_list.append(Eng_all)

                        # 总员级人数
                        Tech_all = TechGL + TechZZ
                        row_data_list.append(Tech_all)

                        # 总常设人数
                        CS_all = Eng_all + Tech_all
                        row_data_list.append(CS_all)

                        # 浪花人力(师级)
                        Eng_support_On = EEmployee.objects.filter(e_status__exact=u'在職', e_category__exact=u'支援',
                                                                  e_grade__contains=u'師', e_leader__exact=leader_ename,
                                                                  e_functionteam__exact=f_row)
                        Eng_support_Off = EEmployee.objects.filter(e_status__exact=u'離職', e_category__exact=u'支援',
                                                                   e_grade__contains=u'師', e_leader__exact=leader_ename,
                                                                   e_functionteam__exact=f_row, e_lastdate__gt=sreach_time)
                        Eng_support = Eng_support_On.count() + Eng_support_Off.count()

                        row_data_list.append(Eng_support)

                        # 浪花人力(员级)
                        Tech_support_On = EEmployee.objects.filter(e_status__exact=u'在職', e_category__exact=u'支援',
                                                                   e_grade__contains=u'員', e_leader__exact=leader_ename,
                                                                   e_functionteam__exact=f_row)
                        Tech_support_Off = EEmployee.objects.filter(e_status__exact=u'離職', e_category__exact=u'支援',
                                                                    e_grade__contains=u'員', e_leader__exact=leader_ename,
                                                                    e_functionteam__exact=f_row, e_lastdate__gt=sreach_time)
                        Tech_support = Tech_support_On.count() + Tech_support_Off.count()

                        row_data_list.append(Tech_support)

                        # 浪花人力(借用员级)
                        Tech_second_On = EEmployee.objects.filter(e_status__exact=u'在職', e_category__exact=u'借調',
                                                                  e_grade__contains=u'員', e_leader__exact=leader_ename,
                                                                  e_functionteam__exact=f_row)
                        Tech_second_Off = EEmployee.objects.filter(e_status__exact=u'離職', e_category__exact=u'借調',
                                                                   e_grade__contains=u'員', e_leader__exact=leader_ename,
                                                                   e_functionteam__exact=f_row, e_lastdate__gt=sreach_time)
                        Tech_second = Tech_second_On.count() + Tech_second_Off.count()
                        row_data_list.append(Tech_second)

                        # 总人数
                        row_data_list.append(CS_all + Eng_support + Tech_support + Tech_second)

                        # 招募状态(需求)
                        subject_data = ESubject.objects.filter(edepartment_id__isnull=False)
                        subject_list = []
                        for s_sub in subject_data:
                            sub_fonc = EEmployee.objects.get(e_id__exact=s_sub.s_leadernum).e_functionteam
                            if sub_fonc == f_row:
                                subject_list.append(s_sub.s_subject)

                        recruit_data = EDemand.objects.filter(d_department__in=subject_list,
                                                              d_application__gte=sreach_time_start,
                                                              d_application__lte=sreach_time_end)
                        demand_num = sum([obj_row.d_amount for obj_row in recruit_data])
                        demand_all += demand_num
                        recruiting_num = ERecruit.objects.filter(r_status__exact=u'進行中').count()
                        recruiting_all += recruiting_num
                        employment_num = sum([obj_row.d_offer for obj_row in recruit_data])
                        employment_all += employment_num
                        surplus_num = sum([obj_row.d_requirement for obj_row in recruit_data])
                        surplus_all += surplus_num
                        row_data_list.append(demand_num)
                        row_data_list.append(demand_all)
                        row_data_list.append(recruiting_num)
                        row_data_list.append(recruiting_all)
                        row_data_list.append(employment_num)
                        row_data_list.append(employment_all)
                        row_data_list.append(surplus_num)
                        row_data_list.append(surplus_all)

                        # 离职人数
                        Eng_leave = EEmployee.objects.filter(e_status__exact=u'離職',
                                                             e_grade__contains=u'師', e_leader__exact=leader_ename,
                                                             e_functionteam__exact=f_row, e_lastdate__lt=sreach_time).count()
                        Tech_leave = EEmployee.objects.filter(e_status__exact=u'離職',
                                                              e_grade__contains=u'員', e_leader__exact=leader_ename,
                                                              e_functionteam__exact=f_row, e_lastdate__lt=sreach_time).count()
                        leave_all = Eng_leave + Tech_leave
                        row_data_list.append(Eng_leave)
                        row_data_list.append(Tech_leave)
                        row_data_list.append(leave_all)

                        # 2015 F1 Approved HC
                        try:
                            team_id = ETeam.objects.get(t_team__exact=f_row).t_id
                        except Exception as e:
                            print e

                        HC2015_obj = EProvide.objects.filter(p_leader__exact='2015 F1 Approved HC', eteam__exact=team_id)
                        if len(HC2015_obj) > 0:
                            HC2015_obj = HC2015_obj[0]
                            HC2015_Num = HC2015_obj.p_engineers + HC2015_obj.p_technician
                        else:
                            HC2015_Num = 0
                        row_data_list.append(HC2015_Num)

                        # 2018 F1 Approved HC
                        HC2018_obj = EProvide.objects.filter(p_leader__exact='2018 F1 Approved HC', eteam__exact=team_id)
                        if len(HC2018_obj) > 0:
                            HC2018_obj = HC2018_obj[0]
                            HC2018_Num = HC2018_obj.p_engineers + HC2018_obj.p_technician
                        else:
                            HC2018_Num = 0
                        row_data_list.append(HC2018_Num)

                        # 2017/9 实际(高峰)人力
                        HC2017_obj = EProvide.objects.filter(p_leader__exact=u'2017/9 實際(高峰)人力', eteam__exact=team_id)
                        if len(HC2017_obj):
                            HC2017_obj = HC2017_obj[0]
                            HC2017_Num = HC2017_obj.p_engineers + HC2017_obj.p_technician
                        else:
                            HC2017_Num = 0
                        row_data_list.append(HC2017_Num)

                        # 2018 FX Approved HC
                        HCFX_obj = EProvide.objects.filter(p_leader__exact='2018 FX Approved HC', eteam__exact=team_id)
                        if len(HCFX_obj) > 0:
                            HCFX_obj = HCFX_obj[0]
                            HCFX_Num = HCFX_obj.p_engineers + HCFX_obj.p_technician
                        else:
                            HCFX_Num = 0
                        row_data_list.append(HCFX_Num)

                        # Magma Approved HC
                        Magma_obj = EProvide.objects.filter(p_leader__exact='Magma Approved HC', eteam__exact=team_id)
                        if len(Magma_obj) > 0:
                            Magma_obj = Magma_obj[0]
                            Magma_Num = Magma_obj.p_engineers + Magma_obj.p_technician
                        else:
                            Magma_Num = 0
                        row_data_list.append(Magma_Num)

                        foc_data_dic[f_row] = row_data_list
                    for f_row in fonction_list:
                        if f_row == 'Inventory':
                            continue
                        foc_data_dic[f_row][1] = leader_EngGL_all
                        foc_data_dic[f_row][3] = leader_EngZZ_all
                        foc_data_dic[f_row][5] = leader_EngTG_all
                        foc_data_dic[f_row][7] = leader_TechGL_all
                        foc_data_dic[f_row][9] = leader_TechZZ_all
                        foc_data_dic[f_row][18] = demand_all
                        foc_data_dic[f_row][20] = recruiting_all
                        foc_data_dic[f_row][22] = employment_all
                        foc_data_dic[f_row][24] = surplus_all

                    group_dir[g_row.l_group][leader_ename] = foc_data_dic

                index_list = [1, 3, 5, 7, 9, 18, 20, 22, 24]
                EERF_Total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                for group_key in group_dir.keys():
                    Group_Total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                   0, 0]
                    Group_sub_dic = group_dir[group_key]
                    for leader_key in Group_sub_dic.keys():
                        for team_key, team_list in Group_sub_dic[leader_key].items():
                            for item_index, item_value in enumerate(team_list):
                                Group_Total[item_index] += item_value
                                EERF_Total[item_index] += item_value
                    for index_r in index_list:
                        Group_Total[index_r] = Group_Total[index_r - 1]
                    group_dir[group_key]['Total'] = Group_Total

                for index_e in index_list:
                    EERF_Total[index_e] = EERF_Total[index_e - 1]
                group_dir['EERF Total'] = EERF_Total
                group_dir['Magma'] = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      0, 0, 0]
                # print 'group_dir:', group_dir
                # 数据存入redis
                for i in group_dir.keys():
                    r.hset(get_html_time, i, str(group_dir[i]))
        else:
            # 获取查找的时间
            sreach_time = datetime.datetime.strptime(get_html_time, '%Y-%m-%d')
            yesterday_time = sreach_time - timedelta(days=1)
            yesterday_time_str = datetime.datetime.strftime(yesterday_time, '%Y-%m-%d')
            # 取昨天数据
            group_dir['EERF Total'] = eval(r.hget(yesterday_time_str, 'EERF Total'))
            group_dir['Magma'] = eval(r.hget(yesterday_time_str, 'Magma'))
            group_dir['default_factory'] = {}
            group_dir['Group1'] = eval(r.hget(yesterday_time_str, 'Group1'))
            group_dir['Group2'] = eval(r.hget(yesterday_time_str, 'Group2'))
            group_dir['Group3'] = eval(r.hget(yesterday_time_str, 'Group3'))

        return HttpResponse(json.dumps(group_dir))


def user_manage(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    用户管理页面
    :param req:
    :return:
    """
    username = req.COOKIES.get('eerf_user', '')
    if username:
        return render_to_response('NPI_EERF/User_manage.html', {'username': username})
    else:
        return HttpResponseRedirect('/login/')


@csrf_exempt
def user_manage_ajax(req):
    """
    :Author: F1233225
    :Date: 2019-01-09
    用户管理界面的 用户的增删改查，根据前台传递的参数进行对应的操作
    :param req:
    :return:
    """
    all_id = []
    for emp in EEmployee.objects.all():
        all_id.append(emp.e_id)
    # 查
    if req.POST.get('message') == 'search':
        search_value = req.POST.get('search_value')
        the_employee_info = {}
        try:
            the_employee = EEmployee.objects.get(e_id__exact=search_value)
            the_employee_info['id'] = the_employee.e_id
            the_employee_info['cname'] = the_employee.e_cname
            the_employee_info['pwd'] = the_employee.e_pwd
            the_employee_info['chmod'] = the_employee.e_chmod
            the_employee_info['adduser'] = the_employee.e_adduser
        finally:
            return HttpResponse(json.dumps(the_employee_info))
    # 改
    if req.POST.get('message') == 'update':
        # print 'update request'
        search_id = split_para(req.POST.get('id_value'))
        pwd_list = split_para(req.POST.get('pwd_value'))
        chmod_list = split_para(req.POST.get('chmod_value'))
        for i in range(len(search_id)):
            the_employee = EEmployee.objects.get(e_id__exact=search_id[i])
            the_employee.e_pwd = pwd_list[i]
            the_employee.e_chmod = chmod_list[i]
            the_employee.save()
        return HttpResponse(json.dumps('success'))
    # 增
    if req.POST.get('message') == 'add':
        id_value = split_para(req.POST.get('id_value'))
        repeat_id = []
        for id in id_value:
            if id in all_id:
                repeat_id.append(id)
        cname_vlaue = split_para(req.POST.get('cname_value'))
        pwd_vlaue = split_para(req.POST.get('pwd_value'))
        chmod_vlaue = split_para(req.POST.get('chmod_value'))
        if len(repeat_id) == 0:
            for i in range(len(id_value)):
                new_employee = EEmployee.objects.create(e_id=id_value[i], e_cname=cname_vlaue[i], e_pwd=pwd_vlaue[i],
                                                        e_chmod=chmod_vlaue[i], e_adduser='add')
        return HttpResponse(json.dumps(repeat_id))
    # 删
    if req.POST.get('message') == 'delete':
        del_id = split_para(req.POST.get('del_id'))
        for id in del_id:
            EEmployee.objects.get(e_id__exact=id).delete()
        return HttpResponse(json.dumps('delete'))


@csrf_exempt
def maintain(req):
    """系统维护"""
    return render_to_response('NPI_EERF/Maintain.html')
