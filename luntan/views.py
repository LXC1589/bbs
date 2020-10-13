from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django import forms
from django.forms import widgets
from django.contrib import auth
from luntan.models import Users as User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.core.mail import send_mail, send_mass_mail

@login_required
def index(request):     # 首页
    print(request.user)
    print("request.user.username", request.user.username)  # request.user.username 获取 request.user 这个对象（记录）的username对应的值
    print("is_anonymous", request.user.is_anonymous)   # request.user.is_anonymous：判断是否为匿名用户

    if not request.user.is_authenticated:
        messages.success(request, "请先登录")
        return redirect("/login/")

    return render(request, "index.html")

# 个人信息页
def personal_info(request):
    if not request.user.is_authenticated:
        messages.success(request, "请先登录")
        return redirect("/login/")
    else:
        username = request.user.username
        email = request.user.email
        # idcard = user.idcard  # 身份证号（要改）

        return render(request, "personal_info.html", locals())


global counter
counter=0
#登录方法
def login(request):

    global counter


    if request.method == "POST":
        username = request.POST.get("user")
        psw = request.POST.get("psw")

        print(username)
        print(psw)

        auth_obj = auth.authenticate(request, username=username, password=psw)
        if auth_obj:
            # 需要auth验证cookie
            auth.login(request, auth_obj)
        user = auth.authenticate(username=username, password=psw)
        # 如果 验证成功 返回 user 对象（就是 auth_user 这张表中的一条记录对象），否则返回None

        email = request.user.email  # 导入邮箱
        print(email)


        print(user)
        if user:
            auth.login(request, user)
            counter=0
            return redirect("/index/")
        else:
            messages.success(request, "用户名或密码错误")
            counter=counter+1 #多次登录提醒
            print(counter)
            if counter >= 3:
                # 发送邮件提示密码已经重置

                subject = '多次尝试登录提醒'
                message = '''
                                                           {}您好，您的账户被多次尝试登录，请检查您的账户密码是否泄露。

                                                                                     开发团队
                                                           '''.format(username)
                send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER,
                          recipient_list=[email, ])


    return render(request, "login.html")


def logout(request):
    # 注销接口：auth.logout(request)
    auth.logout(request)  # 作用等同于： request.session.flush()；# 会把 django_session 表中 相应的记录删除

    return redirect("/login/")

#重置密码方法
def reset_psw(request):
    if request.method == "POST":
        print(request.POST)
        form1 = ResetPswForm(request.POST)

        if form1.is_valid():
            name = form1.cleaned_data.get('name')
            email = form1.cleaned_data.get('email')
            user_id=form1.cleaned_data.get('user_id')

            print(form1.cleaned_data)

            if name and email:
                psw = form1.cleaned_data.get('psw')
                r_psw = form1.cleaned_data.get('r_psw')
                if psw == r_psw:
                    psw = make_password(psw)
                    User.objects.filter(username=name, email=email,user_id=user_id).update(password=psw)

                    # 发送邮件提示密码已经重置
                    subject = '论坛密码重置提醒'
                    message = '''
                                           {}您好，您的密码已经重置
                                           
                                                                     论坛开发团队
                                           '''.format(name)
                    send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER,
                              recipient_list=[email, ])

                    return redirect("/login/")
                else:
                    print(form1.cleaned_data)
                    print(form1.errors)
                    print(type(form1.errors))
        else:
            print(form1.cleaned_data)
            print(form1.errors)
            print(type(form1.errors))

            # 先把全局钩子的异常类型获取到
            err = form1.errors.get("__all__")  # 获取全局钩子的错误信息
            # 同时要在 reg.html 中专门把此错误信息放到 r_psw后面
            return render(request, "reset_psw.html", locals())

    form1 = UserForm()
    return render(request, "reset_psw.html", locals())

class ResetPswForm(forms.Form):
    #注册信息格式要求
    name = forms.CharField(min_length=4, label="用户名", error_messages={"required": "该字段不能为空"},
                           widget=widgets.TextInput(attrs={"class": "form-control"}))  # name这个字段必须是最少为4位的字符串
    psw = forms.CharField(min_length=4, label="新的密码", error_messages={"required": "该字段不能为空"},
                          widget=widgets.PasswordInput(attrs={"class": "form-control"}))
    r_psw = forms.CharField(min_length=4, label="确认密码", error_messages={"required": "该字段不能为空"},
                            widget=widgets.PasswordInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label="邮箱", widget=widgets.EmailInput(attrs={"class": "form-control"}),
                             error_messages={"required": "该字段不能为空", "invalid": "邮箱格式错误"})  # forms.EmailField()：邮箱校验规则
    user_id = forms.CharField(min_length=18, label="身份证号（长度等于18）",
                              error_messages={"required": "该字段不能为空", "min_length": "您的信息格式错误"},
                              widget=widgets.TextInput(attrs={"class": "form-control"}))  # 身份证号
    # 按照局部钩子校验字段


    #数据库信息匹配
    def clean_name(self):  # 只能叫 clean_字段名
        # 根据源码可知， 能执行 clean_字段 方法，说明已经通过了上面的 字段=校验规则 的校验

        # 校验用户名是否重名
        val = self.cleaned_data.get("name")
        # 从数据库中读取数据
        ret = User.objects.filter(username=val)

        if ret:
            return val
        else:
            raise ValidationError("用户名不存在")  # 抛出的异常名必须是 ValidationError；抛出的错误会放到 错误字典中

    def clean_email(self):
        # 校验邮箱是否存在
        val = self.cleaned_data.get("email")
        # 从数据库中读取数据
        ret = User.objects.filter(email=val)

        if ret:
            return val
        else:
            raise ValidationError("邮箱不存在")  # 抛出的异常名必须是 ValidationError；抛出的错误会放到 错误字典中

    def clean_user_id(self):
        # 校验邮箱是否存在
        val = self.cleaned_data.get("user_id")
        # 从数据库中读取数据
        ret = User.objects.filter(user_id=val)

        if ret:
            return val
        else:
            raise ValidationError("身份证号错误或不存在")  # 抛出的异常名必须是 ValidationError；抛出的错误会放到 错误字典中


    def clean(self):
        # 校验 psw 和 r_psw 是否一致
        psw = self.cleaned_data.get("psw")
        r_psw = self.cleaned_data.get("r_psw")

        # 先判断字段是否通过 字段校验和局部钩子，如果没有，则不进行全局钩子校验
        if psw and r_psw:
            if psw == r_psw:
                return self.cleaned_data  # 通过全局钩子校验，则把 cleaned_data 原封返回
            else:
                raise ValidationError("两次密码不一致！")  # 全局钩子的错误字典的形式：{"__all__":[....]}，其key是 "__all__"；这个异常类型不能通过 字段 获取到

        else:  # 没通过字段校验和局部钩子，则把 干净的数据 clean_data 原封不动返回
            return self.cleaned_data



class UserForm(forms.Form):
    #注册信息格式要求
    name = forms.CharField(min_length=4, label="用户名（长度不小于4）", error_messages={"required": "该字段不能为空", "min_length":"您的用户名长度小于4"},
                           widget=widgets.TextInput(attrs={"class": "form-control"}))  # name这个字段必须是最少为4位的字符串
    psw = forms.CharField(min_length=4, label="密码（长度不小于4）", error_messages={"required": "该字段不能为空", "min_length":"您的密码长度小于4"},
                          widget=widgets.PasswordInput(attrs={"class": "form-control"}))
    r_psw = forms.CharField(min_length=4, label="确认密码", error_messages={"required": "该字段不能为空"},
                            widget=widgets.PasswordInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label="邮箱（示例：abc@qq.com）", widget=widgets.EmailInput(attrs={"class": "form-control"}),
                             error_messages={"required": "该字段不能为空", "invalid": "邮箱格式错误"})  # forms.EmailField()：邮箱校验规则
    user_id =forms.CharField(min_length=18, label="身份证号（长度等于18）", error_messages={"required": "该字段不能为空", "min_length":"您的信息格式错误"},
                           widget=widgets.TextInput(attrs={"class": "form-control"}))  # 身份证号
    #按照局部钩子校验字段

    #数据库信息匹配
    def clean_name(self):  # 只能叫 clean_字段名
        # 根据源码可知， 能执行 clean_字段 方法，说明已经通过了上面的 字段=校验规则 的校验

        # 校验用户名是否重名
        val = self.cleaned_data.get("name")
        # 从数据库中读取数据
        ret = User.objects.filter(username=val)

        if not ret:
            return val  # 根据源码可知， return的 val 依然是 name 字段对应的值
        else:
            raise ValidationError("用户名已注册")  # 抛出的异常名必须是 ValidationError；抛出的错误会放到 错误字典中




    def clean_email(self):  # 只能叫 clean_字段名
        # 根据源码可知， 能执行 clean_字段 方法，说明已经通过了上面的 字段=校验规则 的校验

        # 校验邮箱是否重复
        val = self.cleaned_data.get("email")
        # 从数据库中读取数据
        ret = User.objects.filter(email=val)

        if not ret:
            return val  # 根据源码可知， return的 val 依然是 email 字段对应的值
        else:
            raise ValidationError("邮箱已注册")  # 抛出的异常名必须是 ValidationError；抛出的错误会放到 错误字典中


    def clean_user_id(self):  # 只能叫 clean_字段名
        # 根据源码可知， 能执行 clean_字段 方法，说明已经通过了上面的 字段=校验规则 的校验

        # 校验身份证号是否重复
        val = self.cleaned_data.get("user_id")
        # 从数据库中读取数据
        ret = User.objects.filter(user_id=val)

        if not ret:
            return val  # 根据源码可知， return的 val 依然是 user_id 字段对应的值
        else:
            raise ValidationError("身份证已注册")  # 抛出的异常名必须是 ValidationError；抛出的错误会放到 错误字典中



    # clean()：全局钩子；其它所有的校验规则校验完之后，才会走 clean()
    def clean(self):
        # 校验 psw 和 r_psw 是否一致
        psw = self.cleaned_data.get("psw")
        r_psw = self.cleaned_data.get("r_psw")

        # 先判断字段是否通过 字段校验和局部钩子，如果没有，则不进行全局钩子校验
        if psw and r_psw:
            if psw == r_psw:
                return self.cleaned_data  # 通过全局钩子校验，则把 cleaned_data 原封返回
            else:
                raise ValidationError("两次密码不一致！")  # 全局钩子的错误字典的形式：{"__all__":[....]}，其key是 "__all__"；这个异常类型不能通过 字段 获取到

        else:  # 没通过字段校验和局部钩子，则把 干净的数据 clean_data 原封不动返回
            return self.cleaned_data


# 注册方法
def reg(request):
    if request.method == "POST":
        print(request.POST)
        form1 = UserForm(request.POST)

        if form1.is_valid():
            name = form1.cleaned_data.get('name')
            email = form1.cleaned_data.get('email')
            password = form1.cleaned_data.get('psw')
            user_id = form1.cleaned_data.get('user_id')

            User.objects.create_user(username=name, email=email, password=password,user_id=user_id)
            print(form1.cleaned_data)
            # 发送邮件
            subject = '论坛激活邮件'
            message = '''
                       欢迎来到**论坛！亲爱的用户请赶快激活使用吧！
                       {}您好，您的密码为{}
                       <br><a href='http://127.0.0.1:8000/login/'>点击激活登录</a>
                       <br>
                       如果链接不可用请复制以下内容到浏览器激活：
                       http://127.0.0.1:8000/login/
                                                 论坛开发团队
                       '''.format(name,password)
            send_mail(subject=subject, message="", from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[email, ], html_message=message)
            return redirect("/active/")
        else:
            print(form1.cleaned_data)
            print(form1.errors)
            print(type(form1.errors))

            # 先把全局钩子的异常类型获取到
            err = form1.errors.get("__all__")  # 获取全局钩子的错误信息
            # 同时要在 reg.html 中专门把此错误信息放到 r_psw后面
            return render(request, "reg.html", locals())
    form1 = UserForm()
    return render(request, "reg.html", locals())


def active(request):

    return render(request,"active.html",locals())