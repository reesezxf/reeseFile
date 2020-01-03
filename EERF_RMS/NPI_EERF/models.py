# coding:utf-8
from django.db import models


# Create your models here.
# 存放处级单位的基本信息
class EBureau(models.Model):
    b_id = models.IntegerField(primary_key=True)
    # 处的名称
    b_bureau = models.CharField(max_length=64, unique=True)
    # 直接负责人工号
    b_leadernum = models.CharField(max_length=32)
    # 直接负责人姓名
    b_leader = models.CharField(max_length=32)
    # 处的上一级
    b_up = models.CharField(max_length=32)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'ebureau'


# 存放部级单位基本信息
class EDepartment(models.Model):
    d_id = models.IntegerField(primary_key=True)
    # 部的名字
    d_department = models.CharField(max_length=64, unique=True)
    # 直接负责人工号
    d_leadernum = models.CharField(max_length=32)
    # 直接负责人工号
    d_leader = models.CharField(max_length=32)
    # 所属处的外键
    ebureau = models.ForeignKey(EBureau, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'edepartment'


# 存放科级单位基本信息
class ESubject(models.Model):
    s_id = models.IntegerField(primary_key=True)
    # 科的名称
    s_subject = models.CharField(max_length=64, unique=True)
    # 直接负责人工号
    s_leadernum = models.CharField(max_length=32)
    # 直接负责人姓名
    s_leader = models.CharField(max_length=32)
    # 所属部的外键
    edepartment = models.ForeignKey(EDepartment, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'esubject'


# 存放科与function team 之间的联系
class ESubjectTeam(models.Model):
    st_id = models.IntegerField(primary_key=True)
    # 科的名字
    st_subject = models.CharField(max_length=64, unique=True)
    # function team
    st_team = models.CharField(max_length=32)
    # 厂区
    st_place = models.CharField(max_length=32)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'esubjectteam'


# 存放组级单位基本信息
class EGroup(models.Model):
    g_id = models.IntegerField(primary_key=True)
    # 组的名字
    g_group = models.CharField(max_length=64)
    # 直接负责人工号
    g_leadernum = models.CharField(max_length=32)
    # 直接负责人姓名
    g_leader = models.CharField(max_length=32)
    # 所属科级的外键
    esubject = models.ForeignKey(ESubject, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'egroup'


# 存放线级单位基本信息
class ELine(models.Model):
    l_id = models.IntegerField(primary_key=True)
    # 线的名称
    l_group = models.CharField(max_length=64)
    # 直接负责人工号
    l_leadernum = models.CharField(max_length=32)
    # 直接负责人姓名
    l_leader = models.CharField(max_length=32)
    # 所属组级的外键
    egroup = models.ForeignKey(EGroup, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'eline'


# 存放Group leader和部的联系
class ELeader(models.Model):
    l_id = models.IntegerField(primary_key=True)
    # 直接负责人工号
    l_leadernum = models.CharField(max_length=32, unique=True)
    # 直接负责人姓名
    l_leader = models.CharField(max_length=32)
    # group 名字
    l_group = models.CharField(max_length=32)
    # 所属部ID
    edepartment = models.ForeignKey(EDepartment, null=True)
    # 手动资料中的部的排序
    edepartment_num = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'eleader'


# 存放Function team与部之间的关系
class ETeam(models.Model):
    t_id = models.IntegerField(primary_key=True)
    # function team name
    t_team = models.CharField(max_length=32, unique=True)
    # 所属厂区
    t_place = models.CharField(max_length=32)
    # ELeader 外键
    eleader = models.ForeignKey(ELeader, null=True)
    t_leader = models.CharField(max_length=100)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)
    t_subject_leader = models.CharField(max_length=100)

    class Meta:
        db_table = 'eteam'


# 存放编制人力（由管理员完全手动提供）
class EProvide(models.Model):
    p_id = models.IntegerField(primary_key=True)
    # function team ID
    eteam = models.ForeignKey(ETeam, null=True)
    # 师级人数
    p_engineers = models.IntegerField(blank=True, null=True)
    # 员级人数
    p_technician = models.IntegerField(blank=True, null=True)
    # 确定时间
    p_yeardate = models.DateField(blank=True, null=True)
    # 负责人
    p_leader = models.CharField(max_length=32)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'eprovide'


# 存放每个人的基本信息
class EEmployee(models.Model):
    e_id = models.CharField(primary_key=True, max_length=32)
    # 密码
    e_pwd = models.CharField(max_length=32)
    # 中文名
    e_cname = models.CharField(max_length=32)
    # 资位
    e_grade = models.CharField(max_length=32)
    # 直间接
    e_direct = models.CharField(max_length=32)
    # 干别
    e_difference = models.CharField(max_length=32)
    # 管理职
    e_management = models.CharField(max_length=32)
    # 直属主管
    e_managers = models.CharField(max_length=32)
    # 厂区
    e_place = models.CharField(max_length=32)
    # 所属处
    ebureau = models.ForeignKey(EBureau, null=True)
    # 所属部
    edepartment = models.ForeignKey(EDepartment, null=True)
    # 所属科
    esubject = models.ForeignKey(ESubject, null=True)
    # 所属组
    egroup = models.ForeignKey(EGroup, null=True)
    # 所属线
    eline = models.ForeignKey(ELine, null=True)
    # 是否是DRI
    e_DRI = models.CharField(max_length=32)
    # 拥有的权限（处长、部长）
    e_authority = models.CharField(max_length=32)
    # 就职状态
    e_status = models.CharField(max_length=32)
    # 离职日期
    e_lastdate = models.DateField(blank=True, null=True)
    # 英文名
    e_ename = models.CharField(max_length=32)
    # 年资
    e_seniority = models.IntegerField(blank=True, null=True)
    # 邮箱
    e_email = models.CharField(max_length=64)
    # 办公室分机
    e_phone = models.CharField(max_length=64)
    # 手机号
    e_cellphone = models.CharField(max_length=64)
    # 短号
    e_cornet = models.CharField(max_length=32)
    # 入厂日期
    e_firstdate = models.DateField(blank=True, null=True)
    # 学历
    e_degree = models.CharField(max_length=32)
    # leader 英文名
    e_leader = models.CharField(max_length=32)
    # 所属 function team
    e_functionteam = models.CharField(max_length=32)
    # 人员类型（支援、常设）
    e_category = models.CharField(max_length=32)
    # 浪花人员到期时间
    e_expiringdate = models.DateField(blank=True, null=True)
    # 登录权限
    e_chmod = models.CharField(max_length=32)
    # 从前台添加账号
    e_adduser = models.CharField(max_length=32)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'eemployee'


# 存放兼职信息
class EDeputy(models.Model):
    d_id = models.IntegerField(primary_key=True)
    # 工号
    eemployee = models.ForeignKey(EEmployee, null=True)
    # 管理性质（专职、兼职）
    d_character = models.CharField(max_length=32)
    # 所属处
    d_bureau = models.CharField(max_length=32)
    # 所属部
    d_department = models.CharField(max_length=32)
    # 所属科
    d_subject = models.CharField(max_length=32)
    # 所属组
    d_group = models.CharField(max_length=32)
    # 所属线
    d_line = models.CharField(max_length=32)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'edeputy'


# 存放班别信息
class EClasses(models.Model):
    c_id = models.IntegerField(primary_key=True)
    # 班别代号
    c_code = models.CharField(max_length=32)
    # 班别类型（白班、晚班）
    c_type = models.CharField(max_length=32)
    # 工作时数
    c_hours = models.IntegerField(blank=True, null=True)
    # 第一段上班时间
    c_firstup = models.CharField(max_length=32)
    # 第一段下班时间
    c_firstdown = models.CharField(max_length=32)
    # 第二段上班时间
    c_secondeup = models.CharField(max_length=32)
    # 第二段下班时间
    c_secondedown = models.CharField(max_length=32)
    # 加班开始时间
    c_beginover = models.CharField(max_length=32)
    # 班别描述
    c_description = models.CharField(max_length=256)
    # 班别类别
    c_category = models.CharField(max_length=32)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'eclasses'


# 存放考勤刷卡信息
class ECRD(models.Model):
    c_id = models.IntegerField(primary_key=True)
    # 工号
    eemployee = models.ForeignKey(EEmployee, null=True)
    # 法人
    c_legal = models.CharField(max_length=64)
    # 厂区
    c_plant = models.CharField(max_length=32)
    # 日期
    c_datetime = models.DateField(blank=True, null=True)
    # 日期类型（工作日）
    c_datetype = models.CharField(max_length=32)
    # 班别代码
    c_code = models.CharField(max_length=32)
    # 班别类型
    c_type = models.CharField(max_length=32)
    # 规定上班时间
    c_workcrad = models.CharField(max_length=32)
    # 上班刷卡时间
    c_firstcrad = models.DateField(blank=True, null=True)
    # 规定下班时间
    c_closedcard = models.CharField(max_length=32)
    # 下班刷卡时间
    c_lastcard = models.DateField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'ecrd'


# 存放离职单信息
class EDimission(models.Model):
    d_id = models.IntegerField(primary_key=True)
    # 当前步骤
    d_step = models.CharField(max_length=32)
    # 员工工号
    d_number = models.CharField(max_length=32)
    # 姓名
    d_cname = models.CharField(max_length=32)
    # 部门
    d_department = models.CharField(max_length=64)
    # 资位
    d_grade = models.CharField(max_length=32)
    # 管理职
    d_management = models.CharField(max_length=32)
    # 离职原因1
    d_reason01 = models.CharField(max_length=256)
    # 离职原因2
    d_reason02 = models.CharField(max_length=256)
    # 离职原因3
    d_reason03 = models.CharField(max_length=256)
    # 入厂日期
    d_firstdate = models.DateField(blank=True, null=True)
    # 年资
    d_seniority = models.IntegerField(blank=True, null=True)
    # 核定工作日
    d_lastdate = models.DateField(blank=True, null=True)
    # 申请日期
    d_requestdate = models.DateField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'edimission'


# 存放加班时数统计
class EOverhours(models.Model):
    h_id = models.IntegerField(primary_key=True)
    # 工号
    eemployee = models.ForeignKey(EEmployee, null=True)
    # 厂区
    h_place = models.CharField(max_length=32)
    # 部门
    h_department = models.CharField(max_length=64)
    # 资位
    h_grade = models.CharField(max_length=32)
    # 加班类别
    h_type = models.CharField(max_length=32)
    # 加班年月
    h_yearmouth = models.DateField(blank=True, null=True)
    # 一个月的日期
    h_01 = models.IntegerField(blank=True, null=True)
    h_02 = models.IntegerField(blank=True, null=True)
    h_03 = models.IntegerField(blank=True, null=True)
    h_04 = models.IntegerField(blank=True, null=True)
    h_05 = models.IntegerField(blank=True, null=True)
    h_06 = models.IntegerField(blank=True, null=True)
    h_07 = models.IntegerField(blank=True, null=True)
    h_08 = models.IntegerField(blank=True, null=True)
    h_09 = models.IntegerField(blank=True, null=True)
    h_10 = models.IntegerField(blank=True, null=True)
    h_11 = models.IntegerField(blank=True, null=True)
    h_12 = models.IntegerField(blank=True, null=True)
    h_13 = models.IntegerField(blank=True, null=True)
    h_14 = models.IntegerField(blank=True, null=True)
    h_15 = models.IntegerField(blank=True, null=True)
    h_16 = models.IntegerField(blank=True, null=True)
    h_17 = models.IntegerField(blank=True, null=True)
    h_18 = models.IntegerField(blank=True, null=True)
    h_19 = models.IntegerField(blank=True, null=True)
    h_20 = models.IntegerField(blank=True, null=True)
    h_21 = models.IntegerField(blank=True, null=True)
    h_22 = models.IntegerField(blank=True, null=True)
    h_23 = models.IntegerField(blank=True, null=True)
    h_24 = models.IntegerField(blank=True, null=True)
    h_25 = models.IntegerField(blank=True, null=True)
    h_26 = models.IntegerField(blank=True, null=True)
    h_27 = models.IntegerField(blank=True, null=True)
    h_28 = models.IntegerField(blank=True, null=True)
    h_29 = models.IntegerField(blank=True, null=True)
    h_30 = models.IntegerField(blank=True, null=True)
    h_31 = models.IntegerField(blank=True, null=True)
    h_32 = models.IntegerField(blank=True, null=True)
    h_33 = models.IntegerField(blank=True, null=True)
    h_34 = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'eoverhours'


# 存放人力统计信息
class ETotalmans(models.Model):
    t_id = models.IntegerField(primary_key=True)
    # 数据生成日期（每个月一次）
    t_datetime = models.DateField(blank=True, null=True)
    # 总人数
    t_headcount = models.IntegerField(blank=True, null=True)
    # 在职数
    t_reserve = models.IntegerField(blank=True, null=True)
    # 离职数
    t_leave = models.IntegerField(blank=True, null=True)
    # 常设在职师级
    t_engineers = models.IntegerField(blank=True, null=True)
    # 常设在职员级
    t_technician = models.IntegerField(blank=True, null=True)
    # 支援人数
    t_supporter = models.IntegerField(blank=True, null=True)
    # 借调人数
    t_loan = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'etotalmans'


# 存放招募需求信息
class EDemand(models.Model):
    d_id = models.IntegerField(primary_key=True)
    # 紧急程度
    d_urgency = models.CharField(max_length=32)
    # 需求单号
    d_number = models.CharField(max_length=32)
    # 状态
    d_status = models.CharField(max_length=32)
    # 需求项次（原始数据栏位）
    d_frequency = models.CharField(max_length=32)
    # 处
    d_bureau = models.CharField(max_length=64)
    # 部
    d_department = models.CharField(max_length=64)
    # 部门简称
    d_abbreviation = models.CharField(max_length=32)
    # 需求职位
    d_position = models.CharField(max_length=32)
    # 需求人数
    d_amount = models.IntegerField(blank=True, null=True)
    # 已面试人数
    d_finished = models.IntegerField(blank=True, null=True)
    # 录用人数
    d_offer = models.IntegerField(blank=True, null=True)
    # 待报到人数
    d_unfinish = models.IntegerField(blank=True, null=True)
    # 剩余需求人数
    d_requirement = models.IntegerField(blank=True, null=True)
    # 工作经验
    d_experience = models.CharField(max_length=500)
    # 招募专员
    d_recruiter = models.CharField(max_length=32)
    # 资位要求
    d_grade = models.CharField(max_length=32)
    # 联系方式
    d_cellphone = models.CharField(max_length=64)
    # 学历要求
    d_degree = models.CharField(max_length=32)
    # 工作年限
    d_working = models.CharField(max_length=32)
    # 面试主管1
    d_demand01 = models.CharField(max_length=32)
    # 面试主管2
    d_demand02 = models.CharField(max_length=32)
    # 面试要求
    d_request = models.CharField(max_length=32)
    # 其他特别要求
    d_require = models.CharField(max_length=500)
    # 申请日期
    d_application = models.DateField(blank=True, null=True)
    # 希望到职日
    d_register = models.DateField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'edemand'


# 存放面试进度信息
class ERecruit(models.Model):
    r_id = models.IntegerField(primary_key=True)
    # 作业状态
    r_status = models.CharField(max_length=32)
    # 需求单号
    r_number = models.CharField(max_length=32)
    # 姓名
    r_name = models.CharField(max_length=32)
    # 性别
    r_sex = models.CharField(max_length=32)
    # 身份证号
    r_Idcard = models.CharField(max_length=32)
    # 联系凡事
    r_contact = models.CharField(max_length=32)
    # 面试日期
    r_interview = models.DateField(blank=True, null=True)
    # 应聘事业处
    r_bureau = models.CharField(max_length=64)
    # 应聘单位
    r_department = models.CharField(max_length=64)
    # 应聘职位
    r_position = models.CharField(max_length=32)
    # 需求主管1
    r_demand01 = models.CharField(max_length=32)
    # 需求主管2
    r_demand02 = models.CharField(max_length=32)
    # 简历来源
    r_source = models.CharField(max_length=32)
    # 招募专员
    r_recruiter = models.CharField(max_length=32)
    # 学历
    r_degree = models.CharField(max_length=32)
    # 预核资位
    r_grade = models.CharField(max_length=32)
    # 面试主管1结果
    r_result01 = models.CharField(max_length=32)
    # 面试主管2结果
    r_result02 = models.CharField(max_length=32)
    # 签核进度
    r_progress = models.CharField(max_length=32)
    # 体检日期
    r_healthcheck = models.DateField(blank=True, null=True)
    # 体检结果
    r_checkresult = models.CharField(max_length=32)
    # 报到日期
    r_register = models.DateField(blank=True, null=True)
    # 异常备注
    r_anomaly = models.CharField(max_length=32)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'erecruit'


# 存放function team的leader信息
class EHumans(models.Model):
    h_id = models.IntegerField(primary_key=True)
    # 主管名字
    h_cname = models.CharField(max_length=32)
    # 工号
    h_num = models.CharField(max_length=32)
    # 英文名
    h_ename = models.CharField(max_length=32)
    # 属于哪个group
    h_group = models.CharField(max_length=32)
    # 属于哪个function team
    h_team = models.CharField(max_length=32, unique=True)
    # 台干人数
    h_taiwan = models.IntegerField(blank=True, null=True)
    # 中干人数
    h_mesome = models.IntegerField(blank=True, null=True)
    # 员级人数
    h_technician = models.IntegerField(blank=True, null=True)
    # 浪花人数
    h_spindrift = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'ehumans'


# 存放离职率信息
class Eleaveprob(models.Model):
    l_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    l_datetime = models.DateField(blank=True, null=True)
    # 离职率
    l_leaveprob = models.FloatField()
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'eleaveprob'


# 存放离职人数
class Eleavenum(models.Model):
    l_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    l_datetime = models.DateField(blank=True, null=True)
    # 主管
    l_leader = models.CharField(max_length=32)
    # 离职人数
    l_leavenum = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'eleavenum'


# 存放每日工作时数（月均）
class ETimeout(models.Model):
    t_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    t_datetime = models.DateField(blank=True, null=True)
    # 主管
    t_leader = models.CharField(max_length=32)
    # 日工作超过9小时
    t_over9 = models.IntegerField(blank=True, null=True)
    # 日工作超过9.5小时
    t_over95 = models.IntegerField(blank=True, null=True)
    # 日工作超过10小时
    t_over10 = models.IntegerField(blank=True, null=True)
    # 日工作超过10.5小时
    t_over105 = models.IntegerField(blank=True, null=True)
    # 日工作超过11小时
    t_over11 = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'etimeout'


# 存放下班时间点信息
class EGreaterthan(models.Model):
    g_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    g_datetime = models.DateField(blank=True, null=True)
    # 主管
    g_leader = models.CharField(max_length=32)
    # 准点下班
    g_ontime = models.IntegerField(blank=True, null=True)
    # 加班
    g_overtime = models.IntegerField(blank=True, null=True)
    # 工作时长9小时
    g_9_hours = models.IntegerField(blank=True, null=True)
    # 工作时长9.5小时
    g_9_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长10小时
    g_10_hours = models.IntegerField(blank=True, null=True)
    # 工作时长10.5小时
    g_10_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长11小时
    g_11_hours = models.IntegerField(blank=True, null=True)
    # 工作时长11.5小时
    g_11_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长12小时
    g_12_hours = models.IntegerField(blank=True, null=True)
    # 工作时长12.5小时
    g_12_5_hours = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'egreaterthan'


# 存放晚班人次信息
class ENightshift(models.Model):
    n_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    n_datetime = models.DateField(blank=True, null=True)
    # 主管
    n_leader = models.CharField(max_length=32)
    # 晚班人次
    n_number = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'enightshift'


# 存放超时加班时数信息（人均义务加班时数）
class EDutywork(models.Model):
    d_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    d_datetime = models.DateField(blank=True, null=True)
    # 主管
    d_leader = models.CharField(max_length=32)
    # 人均义务加班时数
    d_number = models.IntegerField(blank=True, null=True)
    # 該主管下的常設師級人數
    d_population = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'edutywork'


# 存放调休时数信息
class ERest(models.Model):
    r_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    r_datetime = models.DateField(blank=True, null=True)
    # 工号
    r_employee = models.CharField(max_length=32)
    # G1计薪加班时数
    r_effectivity01 = models.IntegerField(blank=True, null=True)
    # G1超时加班时数
    r_overtime01 = models.IntegerField(blank=True, null=True)
    # G1调休时数
    r_rest01 = models.IntegerField(blank=True, null=True)
    # G2计薪加班时数
    r_effectivity02 = models.IntegerField(blank=True, null=True)
    # G2超时加班时数
    r_overtime02 = models.IntegerField(blank=True, null=True)
    # G2调休时数
    r_rest02 = models.IntegerField(blank=True, null=True)
    # G3计薪加班时数
    r_effectivity03 = models.IntegerField(blank=True, null=True)
    # 夜班天数
    r_nightshift = models.IntegerField(blank=True, null=True)
    # 当月调休时数
    r_totalrest = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'erest'


class EAttendance(models.Model):
    a_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    a_datetime = models.DateField()
    # 工号
    a_employee = models.CharField(max_length=32)  # models.ForeignKey(EEmployee, null=True)
    # 姓名
    a_name = models.CharField(max_length=32)
    # leader
    a_leader = models.CharField(max_length=32)
    # team 员工所属的课
    a_team = models.CharField(max_length=100)
    # 总工作时长
    a_totalhours = models.IntegerField()
    # 工作天数
    a_totaldays = models.IntegerField()
    # 平均工作时长
    a_avghours = models.IntegerField()
    # 最大工作时长
    a_maxhours = models.IntegerField()
    # 总超时时长
    a_totaloverhours = models.IntegerField()
    # 平均超时时长
    a_avgoverhours = models.IntegerField()
    # 最大超时时长
    a_maxoverhours = models.IntegerField()
    # 总义务时长
    a_totaldutyhours = models.IntegerField()
    # 平均义务时长
    a_avgdutyhours = models.IntegerField()
    # 最大义务时长
    a_maxdutyhours = models.IntegerField()
    # 义务工作天数
    a_dutydays = models.IntegerField()
    # 平均白班下班时间
    a_avglastcard = models.CharField(max_length=32)
    # 最晚白班下班时间
    a_maxlastcard = models.CharField(max_length=32)
    # 夜班天数
    a_nightnum = models.IntegerField()
    # 準點下班天數
    a_offduty = models.IntegerField()
    # 非準點下班天數
    a_unoffduty = models.IntegerField()
    # 工作时长超过10.5小时
    a_eighttotal = models.IntegerField()

    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'eattendance'


class ELMFAttendance(models.Model):
    a_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    a_datetime = models.DateField()
    # 工号
    a_employee = models.CharField(max_length=32)  # models.ForeignKey(EEmployee, null=True)
    # 姓名
    a_name = models.CharField(max_length=32)
    # leader
    a_leader = models.CharField(max_length=32)
    # team 员工所属的课
    a_team = models.CharField(max_length=100)
    # 总工作时长
    a_totalhours = models.IntegerField()
    # 工作天数
    a_totaldays = models.IntegerField()
    # 平均工作时长
    a_avghours = models.IntegerField()
    # 最大工作时长
    a_maxhours = models.IntegerField()
    # 总超时时长
    a_totaloverhours = models.IntegerField()
    # 平均超时时长
    a_avgoverhours = models.IntegerField()
    # 最大超时时长
    a_maxoverhours = models.IntegerField()
    # 总义务时长
    a_totaldutyhours = models.IntegerField()
    # 平均义务时长
    a_avgdutyhours = models.IntegerField()
    # 最大义务时长
    a_maxdutyhours = models.IntegerField()
    # 义务工作天数
    a_dutydays = models.IntegerField()
    # 平均白班下班时间
    a_avglastcard = models.CharField(max_length=32)
    # 最晚白班下班时间
    a_maxlastcard = models.CharField(max_length=32)
    # 夜班天数
    a_nightnum = models.IntegerField()
    # 準點下班天數
    a_offduty = models.IntegerField()
    # 非準點下班天數
    a_unoffduty = models.IntegerField()
    # 晚點（8:05后）
    a_eightlate = models.IntegerField()
    # 工作时长超过10.5小时
    a_eighttotal = models.IntegerField()
    # 10:00 后下班天次
    a_tenlate = models.IntegerField()
    # 月份時段
    a_interval = models.CharField(max_length=32)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'elmfattendance'


# 误餐费
class ELateMealFee(models.Model):
    l_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    l_datetime = models.DateField(blank=True, null=True)
    # 員工工號
    l_employee = models.CharField(max_length=32)
    # 員工姓名
    l_cname = models.CharField(max_length=32)
    # 主管
    l_leader = models.CharField(max_length=32)
    # 月份時段
    l_interval = models.CharField(max_length=32)
    # 該年周數
    l_weeknum = models.IntegerField(blank=True, null=True)
    # 當周八點后天數
    l_eightlate = models.IntegerField(blank=True, null=True)
    # 當周九點后天數
    l_ninelate = models.IntegerField(blank=True, null=True)
    # 當周十點后天數
    l_tenlate = models.IntegerField(blank=True, null=True)
    # 當周十一點后天數
    l_elevenlate = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'elatemealfee'


# 存放科级超时加班时数信息（人均义务加班时数）
class ESectionDutywork(models.Model):
    d_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    d_datetime = models.DateField(blank=True, null=True)
    # 科名
    d_section = models.CharField(max_length=32)
    # 人均义务加班时数
    d_number = models.IntegerField(blank=True, null=True)
    # 該科长下的常設師級人數
    d_population = models.IntegerField(blank=True, null=True)
    # 外键关联部级
    d_leader = models.CharField(max_length=32)

    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'esectiondutywork'

# 存放科级晚班人次信息
class ESectionNightshift(models.Model):
    n_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    n_datetime = models.DateField(blank=True, null=True)
    # 科名
    n_section = models.CharField(max_length=32)
    # 晚班人次
    n_number = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'esectionnightshift'

# 存放科级每日工作时数（月均）
class ESectionTimeout(models.Model):
    t_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    t_datetime = models.DateField(blank=True, null=True)
    # 科级名
    t_section = models.CharField(max_length=32)
    # 日工作超过9小时
    t_over9 = models.IntegerField(blank=True, null=True)
    # 日工作超过9.5小时
    t_over95 = models.IntegerField(blank=True, null=True)
    # 日工作超过10小时
    t_over10 = models.IntegerField(blank=True, null=True)
    # 日工作超过10.5小时
    t_over105 = models.IntegerField(blank=True, null=True)
    # 日工作超过11小时
    t_over11 = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'esectiontimeout'

# 存放下班时间点信息
class ESectionGreaterthan(models.Model):
    g_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    g_datetime = models.DateField(blank=True, null=True)
    # 科名
    g_section = models.CharField(max_length=32)
    # 准点下班
    g_ontime = models.IntegerField(blank=True, null=True)
    # 加班
    g_overtime = models.IntegerField(blank=True, null=True)
    # 工作时长9小时
    g_9_hours = models.IntegerField(blank=True, null=True)
    # 工作时长9.5小时
    g_9_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长10小时
    g_10_hours = models.IntegerField(blank=True, null=True)
    # 工作时长10.5小时
    g_10_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长11小时
    g_11_hours = models.IntegerField(blank=True, null=True)
    # 工作时长11.5小时
    g_11_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长12小时
    g_12_hours = models.IntegerField(blank=True, null=True)
    # 工作时长12.5小时
    g_12_5_hours = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'esectiongreaterthan'

# 存放月工作时长信息
class EPersonalWorkTime(models.Model):
    p_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    p_datetime = models.DateField(blank=True, null=True)
    # 主管
    p_leader = models.CharField(max_length=32)
    # 工号
    p_employee = models.CharField(max_length=32)
    # 工作时长9小时
    p_9_hours = models.IntegerField(blank=True, null=True)
    # 工作时长9.5小时
    p_9_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长10小时
    p_10_hours = models.IntegerField(blank=True, null=True)
    # 工作时长10.5小时
    p_10_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长11小时
    p_11_hours = models.IntegerField(blank=True, null=True)
    # 工作时长11.5小时
    p_11_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长12小时
    p_12_hours = models.IntegerField(blank=True, null=True)
    # 工作时长12.5小时
    p_12_5_hours = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'epersonalworktime'

# 存放实时工作时长信息
class ELMFPersonalWorkTime(models.Model):
    p_id = models.IntegerField(primary_key=True)
    # 计算该笔数据的时间
    p_datetime = models.DateField(blank=True, null=True)
    # 主管
    p_leader = models.CharField(max_length=32)
    # 工号
    p_employee = models.CharField(max_length=32)
    # 工作时长9小时
    p_9_hours = models.IntegerField(blank=True, null=True)
    # 工作时长9.5小时
    p_9_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长10小时
    p_10_hours = models.IntegerField(blank=True, null=True)
    # 工作时长10.5小时
    p_10_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长11小时
    p_11_hours = models.IntegerField(blank=True, null=True)
    # 工作时长11.5小时
    p_11_5_hours = models.IntegerField(blank=True, null=True)
    # 工作时长12小时
    p_12_hours = models.IntegerField(blank=True, null=True)
    # 工作时长12.5小时
    p_12_5_hours = models.IntegerField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'elmfpersonalworktime'


class EATTENDANCEANOMALY(models.Model):
    a_id = models.IntegerField(primary_key=True)  # 序号，主键
    a_legal = models.CharField(max_length=64)  # 法人
    a_location = models.CharField(max_length=32)  # 厂区
    a_bureau = models.CharField(max_length=64)  # 處級單位
    a_department = models.CharField(max_length=64)  # 部級單位
    a_class = models.CharField(max_length=64)  # 課級單位
    a_employeeid = models.CharField(max_length=32)  # 工號
    a_name = models.CharField(max_length=32)  # 姓名
    a_datetime = models.DateField(blank=True, null=True)  # 日期
    a_datetype = models.CharField(max_length=32)  # 日期類型
    a_classcode = models.CharField(max_length=32)  # 班別代碼
    a_type = models.CharField(max_length=64)  # 班別類型
    a_workcrad = models.CharField(max_length=32)  # 規定上班時間
    a_firstcrad = models.DateTimeField(blank=True, null=True)  # 上班打卡時間
    a_anomalytype = models.CharField(max_length=32)  # 異常類型1
    a_latetime = models.IntegerField(blank=True, null=True)  # 遲到時長
    a_replytype = models.CharField(max_length=32)  # 回復狀況1
    a_closedcard = models.CharField(max_length=32)  # 規定下班時間
    a_lastcard = models.DateTimeField(blank=True, null=True)  # 下班打卡時間
    a_anomalytype2 = models.CharField(max_length=32)  # 異常類型2
    a_earlytime = models.IntegerField(blank=True, null=True)  # 早退時長
    a_replytype2 = models.CharField(max_length=32)  # 回復狀況2
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'eattendanceanomaly'


class EGSPBYLEADER(models.Model):
    id = models.IntegerField(primary_key=True)  # 序号，主键
    e_leader = models.CharField(max_length=200)  # 領導英文名
    e_functionteam = models.CharField(max_length=200) # 課級信息
    e_closed_num = models.IntegerField(blank=False, null=False) # 金石專案數量
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)
    e_year = models.CharField(max_length=200)  # 年份信息
    e_team_target = models.IntegerField(blank=False, null=False)  # 目標金石
    e_performance = models.IntegerField(blank=False, null=False) # 預估績效
    e_no_closed_num = models.IntegerField(blank=False, null=False)
    e_register_num = models.IntegerField(blank=False, null=False)
    e_team_hc = models.IntegerField(blank=False, null=False) # team人數
    e_per_benefit = models.IntegerField(blank=False, null=False) #
    class Meta:
        db_table = 'egspbyleader'


class ETRAVELCOUNT(models.Model):
    id = models.IntegerField(primary_key=True)  # 序号，主键
    t_leader  = models.CharField(max_length=200)  # 領導英文名
    t_functionteam = models.CharField(max_length=200) # 課級組織名稱
    t_type = models.CharField(max_length=200) # 出差類型
    t_count = models.IntegerField(blank=False, null=False) # 出差天數統計
    t_datetime = models.DateField(blank=True, null=True) # 日期
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'etravelcount'


class EBONUSREPORT(models.Model):
    b_id = models.IntegerField(primary_key=True)  # 序号，主键
    b_team = models.CharField(max_length=200) # 課名
    b_leader = models.CharField(max_length=100) # 部級領導名稱
    b_teamleader = models.CharField(max_length=100) # 課級領導名稱
    b_hr = models.CharField(max_length=200) # HR百分比
    b_gsnum = models.IntegerField(blank=False, null=False) # 金石專案數量
    b_gsweight = models.FloatField(blank=False, null=False) # 金石專案加權得分
    b_gsrate = models.CharField(max_length=200) # 金石完成率
    b_patent = models.IntegerField(blank=False, null=False) # 專利數量
    b_patentweight = models.FloatField(blank=False, null=False) # 專利加權得分
    b_patentrate = models.CharField(max_length=200) # 專利完成率
    b_tax = models.IntegerField(blank=False, null=False) # 稅務抵扣數量
    b_taxweight = models.FloatField(blank=False, null=False) # 稅務抵扣加權得分
    b_proposal = models.CharField(max_length=200) # 智權提案百分比
    b_ee = models.IntegerField(blank=False, null=False) # 客戶EE得分
    b_eepoint = models.FloatField(blank=False, null=False) # 客戶EE得分*人數
    b_idl = models.IntegerField(blank=False, null=False) # 客戶idl評分
    b_customer = models.CharField(max_length=200) # 客戶評分部份百分比
    b_dutywork = models.FloatField(blank=False, null=False) # 月均義務時長
    b_dutyworkhc = models.FloatField(blank=False, null=False) # 月人均義務時長
    b_over10_5 = models.FloatField(blank=False, null=False) # 月均超時10.5人次
    b_over10_5hc = models.FloatField(blank=False, null=False) # 月人均超時10.5人次
    b_night = models.FloatField(blank=False, null=False) # 月均晚班人次
    b_nighthc = models.FloatField(blank=False, null=False) # 月人均晚班天數
    b_travelabroad = models.FloatField(blank=False, null=False) # 月均國外出差天次
    b_travelabroadhc = models.FloatField(blank=False, null=False) # 月人均國外出差天數
    b_travelcn = models.FloatField(blank=False, null=False) # 月均國內出差天數
    b_travelcnhc = models.FloatField(blank=False, null=False) # 月人均國內出差天數
    b_leaveprob = models.CharField(max_length=200) # 離職率
    b_leavepoint = models.FloatField(blank=False, null=False) # 離職率得分
    b_leaverate = models.CharField(max_length=200) # 離職率得分百分比
    b_attendance = models.CharField(max_length=200) # 考勤部份得分百分比
    b_other = models.CharField(max_length=200) # 智權+考勤+客戶評分部份得分百分比
    b_taskforcenum = models.IntegerField(blank=False, null=False) # taskforce數量
    b_taskforce = models.CharField(max_length=200) # taskforce部份得分百分比
    b_total = models.CharField(max_length=200) # 總百分比
    b_money = models.FloatField(blank=False, null=False) #分得金錢
    b_violation = models.FloatField(blank=False, null=False) # 違規罰款
    b_belowquality = models.FloatField(blank=False, null=False) # 英孚未達標罰款
    b_finalymoney = models.FloatField(blank=False, null=False) # 最終所得金錢
    b_datetime = models.DateTimeField(blank=True, null=True) # 創建日期
    b_tablename = models.CharField(max_length=200) # 表名
    b_deldate = models.DateTimeField(blank=True, null=True) # 刪除日期
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)
    b_uuid = models.CharField(max_length=200) # 唯一標識id uuid
    b_datatype = models.CharField(max_length=100)
    b_teamloading = models.CharField(max_length=100)
    b_totalpercentage_lastyear = models.CharField(max_length=100)
    b_totalmoney_lastyear = models.FloatField(blank=False, null=False)
    class Meta:
        db_table = 'ebonusreport'


class E_MANUAL_BOMUS(models.Model):
    m_id = models.IntegerField(primary_key=True)  # 序号，主键
    m_team = models.CharField(max_length=64)
    m_patent_proposal = models.CharField(max_length=64)
    m_patent_closure = models.CharField(max_length=64)
    m_tax_deduction = models.CharField(max_length=64)
    m_task_force = models.CharField(max_length=64)
    m_exceed_expected = models.CharField(max_length=64)
    m_idl = models.CharField(max_length=64)
    m_gold = models.CharField(max_length=64)
    m_datetime = models.DateTimeField(blank=True, null=True)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'e_manual_bomus'


class EBONUSDEPARTMENT(models.Model):
    bd_id = models.IntegerField(primary_key=True)  # 序号，主键
    bd_leader = models.CharField(max_length=100)  # 部級領導名稱
    bd_hr = models.CharField(max_length=200)   # 部級hr
    bd_totalpercentage = models.CharField(max_length=200) # 部級去年的總百分比
    bd_totalmoney = models.FloatField(blank=False, null=False) # 部門分得金錢
    bd_uuid = models.CharField(max_length=200)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)
    bd_violation = models.FloatField(blank=False, null=False)
    bd_belowquality = models.FloatField(blank=False, null=False)

    class Meta:
        db_table='ebonusdepartment'


class EBONUSPERCENTAGE(models.Model):
    bp_id = models.IntegerField(primary_key=True)
    bp_totalmoney = models.FloatField(blank=False, null=False)
    bp_personalmoney = models.FloatField(blank=False, null=False)
    bp_teammoney = models.FloatField(blank=False, null=False)
    bp_othermoney = models.FloatField(blank=False, null=False)
    bp_gsweight_t = models.FloatField(blank=False, null=False)
    bp_gsweight_d = models.FloatField(blank=False, null=False)
    bp_patentweight_t = models.FloatField(blank=False, null=False)
    bp_patentweight_d = models.FloatField(blank=False, null=False)
    bp_taxweight_t = models.FloatField(blank=False, null=False)
    bp_taxweight_d = models.FloatField(blank=False, null=False)
    bp_otherper_t = models.CharField(max_length=200)
    bp_otherper_d = models.CharField(max_length=200)
    bp_taskforceper_t = models.CharField(max_length=200)
    bp_taskforceper_d = models.CharField(max_length=200)
    bp_hrper_d = models.CharField(max_length=200)
    bp_proposal_t = models.CharField(max_length=200)
    bp_proposal_d = models.CharField(max_length=200)
    bp_ee_t = models.CharField(max_length=200)
    bp_ee_d = models.CharField(max_length=200)
    bp_idl_t = models.CharField(max_length=200)
    bp_idl_d = models.CharField(max_length=200)
    bp_duty_t = models.CharField(max_length=200)
    bp_duty_d = models.CharField(max_length=200)
    bp_10_5_t = models.CharField(max_length=200)
    bp_10_5_d = models.CharField(max_length=200)
    bp_night_t = models.CharField(max_length=200)
    bp_night_d = models.CharField(max_length=200)
    bp_travel_abroad_t = models.CharField(max_length=200)
    bp_travel_abroad_d = models.CharField(max_length=200)
    bp_travel_cn_t = models.CharField(max_length=200)
    bp_travel_cn_d = models.CharField(max_length=200)
    bp_leave_t = models.CharField(max_length=200)
    bp_leave_d = models.CharField(max_length=200)
    bp_uuid = models.CharField(max_length=200)
    create_time = models.DateField(auto_now=True, blank=True, null=True)
    edit_time = models.DateField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'ebonuspercentage'
