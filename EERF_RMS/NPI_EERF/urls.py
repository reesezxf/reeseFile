"""EERF URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from NPI_EERF import views

urlpatterns = [
    #     url(r'^admin/', include(admin.site.urls)),
    # url(r'^', views.maintain, name='maintain'),
    url(r'^tip/$',views.tip,name='tip'),
    url(r'^$', views.login, name='login'),
    url(r'^login/$', views.login, name='login'),
    url(r'^update_pwd/$', views.change_pwd, name='change_pwd'),
    #     url(r'^$',views.index,name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^power/$', views.power, name='power'),
    url(r'^unitspower/$', views.unitspower, name='unitspower'),
    url(r'^historypower/$', views.historypower, name='historypower'),
    url(r'^recruit/$', views.recruit, name='recruit'),
    url(r'^dimission/$', views.dimission, name='dimission'),
    url(r'^overwork/$', views.overwork, name='overwork'),
    url(r'^reportform/$', views.reportform, name='reportform'),
    url(r'^overtimework/$', views.overtimework, name='overtimework'),
    url(r'^power_ajax/$', views.power_ajax, name='power_ajax'),
    url(r'^nightwork/$', views.nightwork, name='nightwork'),
    url(r'^eveningtrips/$', views.eveningtrips, name='eveningtrips'),
    url(r'^units_ajax/$', views.units_ajax, name='units_ajax'),
    url(r'^units_setting_ajax/$', views.units_setting_ajax, name='units_setting_ajax'),
    url(r'^download_file/$', views.report_download, name='download_file'),
    url(r'^report_message/$', views.report_message, name='report_messages'),
    url(r'^user_manage/$', views.user_manage, name='user_manage'),
    url(r'^report_message_second/$', views.report_message_second, name='report_message_second'),
    url(r'^report_message_third/$', views.report_message_third, name='report_message_third'),
    url(r'^report_message_four/$', views.report_message_four, name='report_message_four'),
    url(r'^report_message_five/$', views.report_message_five, name='report_message_five'),
    url(r'^user_manage_ajax/$', views.user_manage_ajax, name='user_manage_ajax'),
    url(r'^work_ajax/$', views.work_ajax, name='work_ajax'),
    url(r'^work_section_ajax/$', views.work_section_ajax, name='work_section_ajax'),
    url(r'^report_anomaly/$', views.report_anomaly, name='report_anomaly'),
    # url(r'^bonus_report/$', views.bonus_report, name='bonus_report'),
    url(r'^table_score/$', views.table_score, name='table_score'),
    url(r'^save_bonus/$', views.save_bonus, name='save_bonus'),
    url(r'^get_table_info/$', views.get_table_info, name='get_table_info'),
    url(r'^del_bonus/$', views.del_bonus, name='del_bonus'),
    url(r'^get_bonus_report/$', views.get_bonus_report, name='get_bonus_report'),

]
