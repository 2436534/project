# coding:utf-8
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render,redirect
from .models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template, Context
from django.db import connection, models
from django.contrib.auth import logout,authenticate,login
import datetime, calendar
from  django.template.loader import get_template
import time

import datetime
import hashlib
import sys


ISOTIMEFORMAT="%Y-%m-%d %X"

# Create your views here.
# 主页
def index(request):
	return render(request,'index.html')

# 搜索
def search(request):
	if 'key' in request.GET and 'choice' in request.GET and request.GET['choice'] and request.GET['key']:
		choice = request.GET['choice']
		key = request.GET['key']  # q is an object submitted by front
		# print choice
		if choice == 'h':
			return HttpResponse('/hospitalSearch/' + key +',1,1/')
		elif choice == 'o':
			return HttpResponse('/hospitalSearch/' + key +',2,1/')
		elif choice == 'd':
			return HttpResponse('/doctorSearch/' + key +',1/')
		else:
			return HttpResponse('/')
	else:
		return HttpResponse('/')

# 测试搜索用
def header(request):
	if 'member_id' in request.session and request.session['member_id']:
		user = request.session['member_id']
		res = User.objects.get(id = user)
		name = res.name
	else:
		user = ""
		name = ""
	return render(request,'header.html', {"user":user,"name":name,})# 样本，需要改变

def footer(request):
	return render(request,'footer.html')

# 显示科室信息
def officeinfo(request,officeid,dateid):
	Week = ["日","一","二","三","四","五","六"]
	daytime = ["m","a","e"]
	o_id = officeid
	d_id = dateid
	d = Department.objects.get(id = o_id)
	h = Hospital.objects.get(id = d.hospitalId_id)
	s = datetime.datetime.today()
	w = datetime.datetime.now().weekday() + 1
	visitdate = []
	dateprint = []
	dateweek = []
	num = 1
	while num < 8:
		dateprint.append((s + datetime.timedelta(days=num)).strftime("%m-%d"))
		visitdate.append((s + datetime.timedelta(days=num)).strftime("%Y-%m-%d"))
		dateweek.append(Week[(w+num)%7])
		num = num+1
	# alldoctor = Doctor.objects.filter(departmentId_id = 1)
	record = [["" for x in range(7)] for y in range(3)]
	for i in range(7):
		for j in range(3):
			if j == 0:
				time = "m"
			elif j == 1:
				time = "a"
			elif j == 2:
				time = "e"
			cursor = connection.cursor()
			cursor.execute("""
				SELECT Count(*) FROM OrderAndVisit_visitmessage
				WHERE doctorId_id in (
				SELECT id FROM OrderAndVisit_doctor
				WHERE departmentId_id = '%s') AND
				visitDate = '%s' AND
				visitTime = '%s' AND
				restNumber > 0""" % (o_id,visitdate[i],time))

			row = cursor.fetchone()
			if row[0] > 0:
				record[j][i] = visitdate[i] + daytime[j]
			else:
				record[j][i] = ""
	if d_id:
		visitList = VisitMessage.objects.filter(visitDate=d_id[0:-1], visitTime=d_id[-1],
												doctorId__departmentId_id__exact=o_id, restNumber__gt = 0)
	else:
		visitList = []

	return render(request,'officeinfo.html',{"dateprint":dateprint,"dateweek":dateweek,
												  "morning":record[0], "afternoon":record[1],
												  "evening":record[2],"h":h, "d":d, "d_id":d_id, "o_id":o_id,
												  "visitList":visitList})

# 显示医生信息，单独页面
def doctor(request,did):
	Week = ["日", "一", "二", "三", "四", "五", "六"]
	s = datetime.datetime.today()
	w = datetime.datetime.now().weekday() + 1
	visitdate = []
	dateprint = []
	dateweek = []
	num = 1
	while num < 8:
		dateprint.append((s + datetime.timedelta(days=num)).strftime("%m-%d"))
		visitdate.append((s + datetime.timedelta(days=num)).strftime("%Y-%m-%d"))
		dateweek.append(Week[(w + num) % 7])
		num = num + 1
	#
	visitId = [[False for x in range(7)] for y in range(3)]
	for i in range(7):
		for j in range(3):
			if j == 0:
				time = "m"
			elif j == 1:
				time = "a"
			elif j == 2:
				time = "e"
			cursor = connection.cursor()
			cursor.execute("""
					SELECT id FROM OrderAndVisit_visitmessage
					WHERE doctorId_id = '%s' AND
					visitDate = '%s' AND
					visitTime = '%s' AND
					restNumber > 0""" % (did,visitdate[i], time))

			row = cursor.fetchone()
			if row is not None:
				visitId[j][i] = row
			else:
				visitId[j][i] = False

	m=[]
	for i in visitId[0]:
		m.append(i)
	doc = Doctor.objects.get(id=did)
	dep=Department.objects.get(id=doc.departmentId_id)
	hos=Hospital.objects.get(id=dep.hospitalId.id)

	vis = VisitMessage.objects.filter(doctorId=doc.id)
	vtime = []
	for v in vis:
		vtime.append(v.visitDate)

	return render(request,'doctorinfo.html',{'date': dateprint,'sex':doc.sex,'name':doc.name,'info':doc.introduction,'address':doc.address,'dep':dep.name,'hos':hos.name,'morning':visitId[0],'afternoon':visitId[1],'evening':visitId[2],'week':dateweek} )

#　显示医院信息，单独页面
def hospital(request,hid):
	hos = Hospital.objects.get(id=hid)
	dep = Department.objects.filter(hospitalId=hos.id).order_by("classinfo")
	cursor = connection.cursor()
	cursor.execute("""
					SELECT count( * )
					FROM `OrderAndVisit_doctor`
					WHERE departmentId_id
					IN (
					SELECT id
					FROM `OrderAndVisit_department`
					WHERE hospitalId_id ='%s')
					"""%(hos.id) )

	row = cursor.fetchall()
	cursor.execute("""
	SELECT count( * )
	FROM `OrderAndVisit_ordermessage`
	WHERE visitId_id
	IN (

	SELECT id
	FROM `OrderAndVisit_visitmessage`
	WHERE doctorId_id
	IN (

	SELECT id
	FROM `OrderAndVisit_doctor`
	WHERE departmentId_id
	IN (

	SELECT id
	FROM `OrderAndVisit_department`
	WHERE hospitalId_id = '%s'
	)
	)
	)
	""" % (hos.id))

	peopleNum = cursor.fetchall()
	return render(request,'hosinfo.html',{'name':hos.name,'img':hos.img,'address':hos.address,'phonenum':hos.phonenum,'docnum':row[0][0],'info':hos.introduction,'dep':dep,'peoplen':peopleNum[0][0]})

# 预约挂号，处理函数，跳转到？
def orderInfo(request, vid):
	if 'member_id' in request.session and request.session['member_id']:
		usrid=request.session['member_id']
		visitid=vid
		o_time=time.strftime( ISOTIMEFORMAT, time.localtime(time.time()) )
		vis=VisitMessage.objects.filter(id=vid)
		usr=User.objects.filter(id=usrid)
		if vis[0].restNumber > 0:
			if usr[0].creditLevel > 0:
				# if date < 7
				current_date=datetime.datetime.now().date()
				current_order=OrderMessage.objects.filter(userId=usrid, isCanceled=False)
				flag = True
				for co in current_order:
					order_date=datetime.datetime.strptime(co.visitId.visitDate, "%Y-%m-%d").date()
					date_minus=order_date-current_date
					day_minus=date_minus.days
					if day_minus < 7:
						if day_minus > 0:
							flag = False
				if flag == True:
					rnm=vis[0].restNumber
					VisitMessage.objects.filter(id=vid).update(restNumber=rnm-1)
					cursor = connection.cursor()
					cursor.execute("INSERT INTO OrderAndVisit_ordermessage(userId_id, visitId_id,ordertime) values (%s,%s,%s)",[usrid,visitid,o_time])
					#Error Dealing
					cursor.close()
					msg="预约成功"
				else:
					msg="预约失败, 已经有7天内就诊的有效预约"
			else:
				msg="预约失败，您的信用等级不允许你进行预约"
		else:
			msg="预约失败，剩余号源不足！"
		#print usrid,vid,msg
		direct='/appointinfo/'
		#print direct
		return message_append(request,msg,direct)
	else:
		return message_append(request,"请先登录",'/')

#　取消预约，处理函数，跳转到？
def cancelInfo(request, oid):
	if 'member_id' in request.session and request.session['member_id']:
		o_time=time.strftime( ISOTIMEFORMAT, time.localtime(time.time()) )
		usrid=request.session['member_id']
		visitid=oid
		#Check of time done
		#if order can be canceled
		buf=OrderMessage.objects.filter(id=oid)
		if usrid == buf[0].userId.id:
			current_date=datetime.datetime.now().date()
			bufo=OrderMessage.objects.filter(id=oid)
			order_date=datetime.datetime.strptime(bufo[0].visitId.visitDate, "%Y-%m-%d").date()
			date_minus_c=order_date-current_date
			day_minus_c=date_minus_c.days
			if day_minus_c > 0:
				CF=OrderMessage.objects.filter(id=oid)
				if CF[0].isCanceled == False:
					OrderMessage.objects.filter(id=oid).update(isCanceled=True)
					ToBeCanceledOrder = OrderMessage.objects.filter(id=visitid)
					#SQL
					cursor = connection.cursor()
					cursor.execute("INSERT INTO OrderAndVisit_ordercancelmessage(orderId_id,cancelTime) values (%s,%s)",[visitid,o_time])
					cursor.close()
					#Cope with payment
					msg="取消成功"
				else:
					msg="不可重复操作"
			else:
				msg="取消失败"
		else:
			msg="未知错误"
		direct='/appointinfo/'
		#print direct
		return message_append(request,msg,direct)
	else:
		return message_append(request,"请先登录",'/')

#　支付订单，处理函数，跳转到？
def payInfo(request, oid):
	# 此处visitid指的是订单id
	visitid=oid
	if 'member_id' in request.session and request.session['member_id']: #debug
		usrid = request.session['member_id']
		TF = OrderMessage.objects.filter(id=visitid)
		if usrid == TF[0].userId.id:
			if TF[0].isPayed == False:
				#Update 挂号排位确定
				cnt=OrderMessage.objects.filter(visitId=visitid, isPayed=True).count()
				#print cnt
				cnt=cnt+1
				OrderMessage.objects.filter(id=visitid).update(isPayed=True)
				#SQL
				cursor = connection.cursor()
				cursor.execute("INSERT INTO OrderAndVisit_registermessage(orderNum,orderId_id,visitId_id) values (%s,%s,%s)",[cnt,visitid,TF[0].visitId.id])
				cursor.close()
				return message_append(request,"支付成功",'/appointinfo/')
			else:
				msg="请求处理失败"
			direct='/appointinfo/'
			return message_append(request,msg,direct)
		else:
			return message_append(request,"请先登录",'/')
	else:
		return redirect('/')

# 用户预约信息，单独页面
def appointInfo(request):
	#msg="default"
	#release
	#s_userid = request.user.id
	if 'member_id' in request.session and request.session['member_id']:
		s_userid = request.session['member_id']
		us = User.objects.get(id=s_userid)
		sex = us.sex
		username = us.userName
		orderinfo = OrderMessage.objects.filter(userId=s_userid).order_by('-id')
		return render(request, 'appointinfo.html', {'user': us, 'appointinfo': orderinfo})
	else:
		return redirect('/')

# 用户登录，处理函数，跳转主页
def do_login(request):
	if request.method=="POST":
		userName = request.POST.get('name')
		userPassword=request.POST.get('password')
		res1 = User.objects.filter(userName = userName)
		if not res1:
			return message_append(request, "用户名错误", "/")
		else:
			res = res1[0]
			m = hashlib.md5()
			m.update(userPassword.encode('utf-8'))
			userPassword = m.hexdigest()
			if res.password == userPassword:
				request.session['member_id'] = res.id
				request.session['userName'] = userName
				return redirect("/")
			else:
				return message_append(request, "密码错误", "/")
	else:
		return message_append(request,"非法操作","/")

#　用户注销，处理函数，跳转主页
def dologout(request):
	try:
		del request.session['member_id']
		del request.session['userName']
		logout(request)
		return message_append(request,"注销成功","/")
	except KeyError:
		print("del session failed...")
		return message_append(request,"失败！","/")

# 用户注册，处理函数，跳转主页
# noinspection PyUnreachableCode
def register(request):
	if request.method == 'POST':
		username = request.POST['username']
		name = request.POST['name']
		password = request.POST['password']
		password2 = request.POST['password2']
		sex = request.POST['gender']
		birthDate = request.POST['birthdate']
		idNum = request.POST['idNum']
		phoneNum = request.POST['phoneNum']
		res = User.objects.filter(userName=username)
		if password2 != password:
			return message_append(request,"密码与确认密码不同", "/registerpage/")
		if res:
			return message_append(request, "用户名已存在", "/registerpage/")
		m = hashlib.md5()
		m.update(password.encode('utf-8'))
		password = m.hexdigest()
		user_tmp = User(userName=username, name=name, password=password, sex=sex, birthday=birthDate, telephone=phoneNum, idCard=idNum)
		user_tmp.save()
		res = User.objects.get(userName=username)
		request.session['member_id'] = res.id
		return HttpResponse('注册成功！')
# # 验证手机号
# def mobile_validate(value):
# 	mobile_re = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
# 	if not mobile_re.match(value):
# 		raise ValidationError('手机号码格式错误')
#
# # 验证身份证号
# def IDValidator(value):
# 	# 身份证号码验证
# 	Wi = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
# 	Ti = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
# 	sum = 0
# 	value = value.upper()
# 	if len(value) != 18:
# 		raise ValueError('请输入18位身份证号码,您只输入了%s位' % len(value))
# 	for i in range(17):
# 		sum += int(value[i]) * Wi[i]
# 	if Ti[sum % 11] != value[17]:
# 		raise ValueError('请输入正确的身份证号码')

# 用户注册，单独页面
def registerpage(request):
	return render(request,'register.html')

# 医院列表，单独页面
def hospitalSearch(request,hospitalname,flag,page):
	flagnum=int(flag)
	pagenum=int(page)
	if(pagenum<=0):
		pagenum = 1
	hosstart = 0
	hosend = 0
	pagecounter = 0
	pagestart = 0
	pageend = 0
	flagbool = True
	hospitals = []
	departments = []

	if(flagnum==1):
		flagbool = True
		hospitals = Hospital.objects.filter(name__contains=hospitalname)
	else:
		flagbool = False
		departments = Department.objects.filter(name__contains=hospitalname)
		for department in departments:
			hospitals.append(department.hospitalId)
		# hospitals = departments.hospitalId
		# hospitals =  Hospital.objects.raw('''SELECT *
		#                                     FROM OrderAndVisit_hospital
		#                                     Where id in
		#                                     (SELECT hospitalId_id
		#                                     FROM OrderAndVisit_department
		#                                     WHERE name LIKE '%s')'''%unicode(hospitalname))

	hosnum=0
	docnum=[]
	ordernum=[]
	for hospital in hospitals:
		doctors = Doctor.objects.filter(departmentId__hospitalId__id=hospital.id)
		orders = OrderMessage.objects.filter(visitId__doctorId__departmentId__hospitalId__id=hospital.id)
		hosnum+=1
		tempdocnum=0
		tempordernum=0
		for order in orders:
			tempordernum +=1
		for doctor  in doctors:
			tempdocnum+=1
		docnum.append(tempdocnum)
		ordernum.append(tempordernum)

	#pagecounter
	if(hosnum%4==0):
		pagecounter = hosnum/4
	else:
		pagecounter = hosnum/4+1

	#pagestart end
	if (pagenum - 2 <= 0):
		pagestart = 1
	else:
		pagestart = pagenum - 2
	if (pagenum + 2 > pagecounter):
		pageend = pagecounter + 1
	else:
		pageend = pagenum + 3

	#hos start and end
	if(pagenum*4 <= hosnum):
		hosend = pagenum*4
		hosstart = hosend-4
	else:
		if(hosnum>=4):
			hosend = hosnum+1
			hosstart = (pagecounter-1)*4
		else:
			hosstart = 0
			hosend = hosnum
	hosstart=int(hosstart)
	hosend=int(hosend)
	pagestart=int(pagestart)
	pageend=int(pageend)
	hosinfo=zip(hospitals,docnum,ordernum)
	depinfo=zip(departments,docnum,ordernum) # hosinfo[hosstart:hosend]   [hosstart:hosend]
	return render(request,'search_hospital.html',{'hosinfo': hosinfo,'depinfo': depinfo,'flagbool':flagbool,'pagerange':range(pagestart,pageend),'flag':flag,'hospitalname':hospitalname,'pageend':pagecounter})
 

# 医生列表，单独页面
def doctorSearch(request,doctorname,page):
	doctors = Doctor.objects.filter(name__contains=doctorname).prefetch_related()
	docnum=0
	for doc in doctors:
		docnum += 1
	pagenum=int(page)
	if(pagenum<=0):
		pagenum = 1

	docstart = 0
	docend = 0
	pagecounter = 0
	pagestart = 0
	pageend = 0
	if(docnum%4==0):
		pagecounter = docnum/4
	else:
		pagecounter = docnum/4+1
	if(pagenum-2<=0):
		pagestart = 1
	else:
		pagestart = pagenum-2

	if(pagenum+2>pagecounter):
		pageend = pagecounter+1
	else:
		pageend = pagenum+3

	if (pagenum * 4 <= docnum):
		docend = pagenum*4
		docstart = docend-4

	else:
		if(docnum>=4):
			docend = docnum+1
			docstart = (pagecounter-1)*4
		else:
			docstart = 0
			docend = docnum
	docstart=int(docstart)
	docend=int(docend)
	pagestart=int(pagestart)
	pageend=int(pageend)
	return render(request,'search_doctor.html',{'doctors': doctors[docstart:docend],'pagerange':range(pagestart,pageend),'doctorname':doctorname,'pageend':pagecounter})

# 科室列表，单独页面
def officeSearch(request):
	dep = Department.objects.order_by("classinfo")
	return render(request,'search_office.html',{"dep":dep,})

#　用户信息，单独页面
def myinfo(request):
	if 'member_id' in request.session and request.session['member_id']:
		user_id = request.session['member_id']
		res = User.objects.get(id = user_id)
		if res.sex == 'm':
			sex = '男'
		else:
			sex = '女'
		ret = {
			'name': res.name,
			'sex': sex,
			'idNum': res.idCard,
			'telephone': res.telephone,
			'birthday':res.birthday
		}
		return render (request,'myinfo.html', ret)
	else:
		return redirect('/login')

# 修改密码，处理函数
def changepassword(request):
	if 'member_id' in request.session and request.session['member_id']:
		user_id = request.session['member_id']
		res = User.objects.get(id=user_id)
		if request.method == 'GET':
			if 'oldpassword' in request.GET and 'newpassword' in request.GET and 'newpassword2' in request.GET and request.GET['oldpassword'] and request.GET['newpassword'] and request.GET['newpassword2']:
				o_pass = request.GET['oldpassword']
				n_pass = request.GET['newpassword']
				n_pass2 = request.GET['newpassword2']
				if n_pass != n_pass2:
					return message_append(request, "两次密码输入不同", "/myInfo/")
				m = hashlib.md5()
				m.update(o_pass)
				o_pass = m.hexdigest()
				if res.password != o_pass:
					return message_append(request, "密码错误", "/myInfo/")
				n = hashlib.md5()
				n.update(n_pass)
				n_pass = n.hexdigest()
				res.password = n_pass
				res.save()
				return message_append(request, "修改成功", "/myInfo/")
			else:
				return message_append(request, "请输入密码", "/myInfo/")
		else:
			return message_append(request, "未知错误", "/myInfo/")
	else:
		return HttpResponse('/')

# 弹窗页面
def message_append(request, msg, direct):
	return render(request, 'bkstg_msg.html', {'msg': msg, 'direct': direct})

# 获取当前年份
def getYear():
	return str(datetime.date.today())[0:4]

# 预约单，单独页面
def OrderForm(request, oid):
	if 'member_id' in request.session and request.session['member_id']:
		usrid = request.session['member_id']
		TF = OrderMessage.objects.filter(id=oid)
		if usrid == TF[0].userId.id:
			if TF[0].isCanceled == True:
				return HttpResponse("已取消预约无法打印预约单")
			else:
				hospital=TF[0].visitId.doctorId.departmentId.hospitalId.name
				department=TF[0].visitId.doctorId.departmentId.name
				doctor=TF[0].visitId.doctorId.name
				vdate=TF[0].visitId.visitDate
				vtime=TF[0].visitId.visitTime
				username=TF[0].userId.name
				usersex=TF[0].userId.sex
				idcard=TF[0].userId.idCard
				birthdaystr=idcard[6:10]
				IDCARDDATEFORMAT="%Y"
				now_year=int(getYear())
				birth_day=int(birthdaystr)
				years_minus=now_year-birth_day
				ages=years_minus
				return render(request, 'print_preorder.html', {'hospital':hospital, 'department':department, 'doctor':doctor, 'date':vdate, 'time':vtime, 'name':username, 'sex':usersex, 'age':ages})
		else:
			return HttpResponse("访问非法，无法打印预约单")
	else:
		return HttpResponse('/')

# 挂号单，单独页面
def BookForm(request, oid):
	if 'member_id' in request.session and request.session['member_id']:
		usrid = request.session['member_id']
		TF = OrderMessage.objects.filter(id=oid)
		if usrid == TF[0].userId.id:
			if TF[0].isCanceled == True:
				return HttpResponse("已取消预约无法打印挂号单")
			elif TF[0].isPayed == False:
				return HttpResponse("未支付预约无法打印挂号单")
			else:
				hospital=TF[0].visitId.doctorId.departmentId.hospitalId.name
				department=TF[0].visitId.doctorId.departmentId.name
				doctor=TF[0].visitId.doctorId.name
				vdate=TF[0].visitId.visitDate
				vtime=TF[0].visitId.visitTime
				username=TF[0].userId.name
				usersex=TF[0].userId.sex
				idcard=TF[0].userId.idCard
				birthdaystr=idcard[6:10]
				IDCARDDATEFORMAT="%Y"
				now_year=int(getYear())
				birth_day=int(birthdaystr)
				years_minus=now_year-birth_day
				ages=years_minus
				BookItem = RegisterMessage.objects.filter(orderId=oid)
				booknum=BookItem[0].orderNum
				return render(request, 'print_order.html', {'booknum':booknum, 'hospital':hospital, 'department':department, 'doctor':doctor, 'date':vdate, 'time':vtime, 'name':username, 'sex':usersex, 'age':ages})
		else:
			return HttpResponse("访问非法，无法打印挂号单")
	else:
		return HttpResponse('/')

