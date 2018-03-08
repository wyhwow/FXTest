"""
@author: lileilei
@file: views.py
@time: 2017/7/13 16:42
"""
from app import  app
from  flask import  redirect,request,render_template,session,url_for,flash,make_response,send_from_directory,jsonify
from  app.models import *
from app.form import  *
import os
from flask.views import MethodView,View
from flask_login import current_user,login_required
from app.common.decorators import chckuserpermisson
def get_pro_mo():
    projects=Project.query.all()
    model=Model.query.all()
    return  projects,model
@app.route('/down_jiekou',methods=['GET'])
@login_required
def down_jiekou():
    basedir = os.path.abspath(os.path.dirname(__file__))
    file_dir=os.path.join(basedir,'upload')
    response=make_response(send_from_directory(file_dir,'interface.xlsx',as_attachment=True))
    return response
@app.route('/down_case',methods=['GET'])
@login_required
def down_case():
    basedir = os.path.abspath(os.path.dirname(__file__))
    file_dir=os.path.join(basedir,'upload')
    response=make_response(send_from_directory(file_dir,'interface_case.xlsx',as_attachment=True))
    return response
class LoadView(View):
    methods=['GET']
    def dispatch_request(self,filename):
        basedir = os.path.abspath(os.path.dirname(__file__))
        file_dir=os.path.join(basedir,'upload')
        response=make_response(send_from_directory(file_dir,filename,as_attachment=True))
        return response
class AddmodelView(MethodView):
    def get(self):
        return render_template('add/add_moel.html')
    def post(self):
        model=request.get_data('projectname')
        modelnew=model.decode('utf-8')
        models = Model.query.filter_by(model_name=modelnew).first()
        if models:
            return jsonify({'code': 315,'msg':'模块不能重复存在','data':''})
        new_moel = Model(model_name=modelnew, model_user_id=current_user.id)
        db.session.add(new_moel)
        try:
            db.session.commit()
            return  jsonify({'code':200,'msg':'添加成功','data':''})
        except Exception as e:
            db.session.rollback()
            return jsonify({'code': 316,'msg':'添加失败，原因：%s'%e,'data':''})
class AddproView(MethodView):
    def  get(self):
        return  render_template('add/add_pro.html')
    def post(self):
        if current_user.is_sper is False:
            return jsonify({'code': 317, 'msg': '权限不足！' , 'data': ''})
        model = request.get_data('projectname')
        modelnew = model.decode('utf-8')
        if modelnew =='':
            return jsonify({'code': 329, 'msg': '不能为空！', 'data': ''})
        projec=Project.query.filter_by(project_name=modelnew).first()
        if projec:
            return jsonify({'code': 319, 'msg': '项目不能重复！', 'data': ''})
        new_moel=Project(project_name=modelnew,project_user_id=current_user.id)
        db.session.add(new_moel)
        try:
            db.session.commit()
            return jsonify({'code': 200, 'msg': '添加成功！', 'data': ''})
        except Exception as e:
            db.session.rollback()
            return jsonify({'code': 219, 'msg': '添加失败，原因:%s！'%e, 'data': ''})
class DelemodelView(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self,id):
        next = request.headers.get('Referer')
        model=Model.query.filter_by(id=id).first()
        model.status=True
        db.session.commit()
        flash(u'删除成功')
        return redirect(next or url_for('home.model'))
class DeleproView(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self,id):
        if  current_user.is_sper == False:
            flash('权限不足，不能删除项目')
            return redirect(request.headers.get('Referer'))
        proje=Project.query.filter_by(id=id).first()
        proje.status=True
        db.session.commit()
        flash(u'删除成功')
        return redirect( url_for('home.project'))
class EditmoelView(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self,id):
        model=Model.query.filter_by(id=id).first()
        if request.method=="POST":
            ed_mode=request.form.get('model')
            if ed_mode=='':
                flash(u'请添加模块名')
                return render_template('edit/edit_model.html', mode=model)
            model.model_name=ed_mode
            try:
                db.session.commit()
                flash(u'编辑成功')
                return  redirect(url_for('home.model'))
            except:
                db.session.rollback()
                flash(u'编辑zhi路漫漫兮')
                return redirect(url_for('home.model'))
        return  render_template('edit/edit_model.html', mode=model)
class EditproView(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self,id):
        if current_user.is_sper==False:
            flash('权限不足,')
            return  redirect(url_for('home.project'))
        project=Project.query.filter_by(id=id).first()
        if request.method=="POST":
            ed_mode=request.form.get('project')
            if ed_mode=='':
                flash(u'请添加项目')
                return render_template('edit/edit_pro.html', project=project)
            project.project_name=ed_mode
            try:
                db.session.commit()
                flash(u'编辑成功')
                return  redirect(url_for('home.project'))
            except:
                db.session.rollback()
                flash(u'编辑出现小异常')
                return redirect(url_for('home.project'))
        return  render_template('edit/edit_pro.html', project=project)
class DeleteResultView(View):
    methods=['GET','POST']
    @login_required
    def dispatch_request(self,id):
        if chckuserpermisson() == False:
            flash('权限不足，不能删除测试报告')
            return  redirect(request.headers.get('Referer'))
        delTest=TestResult.query.filter_by(id=id).first()
        delTest.status=True
        db.session.commit()
        flash(u'删除成功')
        return redirect( url_for('home.test_rep'))
class ADDTesteventView(MethodView):#添加测试环境
    @login_required
    def get(self):
        if current_user.is_sper == True:
            projects=Project.query.filter_by(status=False).order_by('-id').all()
        else:
            projects=[]
            for i in current_user.quanxians:
                if  (i.projects in id)==False:
                    projects.append(i.projects)
        if len(projects)<=0:
            flash(u'你没有所属的项目，请在后台添加')
            return redirect(url_for('home.ceshihuanjing'))
        forms=Interface_Env()
        return render_template('add/add_even.html', form=forms, projects=projects)
    @login_required
    def post(self):
        data=request.get_json()
        url_old=Interfacehuan.query.filter_by(url=str(data['url'])).first()
        if url_old:
            return  jsonify({"msg":u'测试环境必须是相互独立的',"code":209,'data':''})
        prkcyt=Project.query.filter_by(project_name=data['work']).first()
        end=Interfacehuan()
        end.url=data['url']
        end.desc=data['desc']
        end.project=prkcyt.id
        end.database=data['database']
        end.databaseuser=data['databaseuser']
        end.databasepassword=data['databasepassword']
        end.make_user=current_user.id
        db.session.add(end)
        try:
            db.session.commit()
            return jsonify({"msg": u'添加测试环境成功!', "code": 200, 'data': ''})
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": u'添加测试用例失败！原因：%s'%e, "code": 211, 'data': ''})
class DeleteEventViews(MethodView):#删除测试环境
    @login_required
    def get(self,id):
        next = request.headers.get('Referer')
        event=Interfacehuan.query.filter_by(id=id).first()
        event.status=True
        db.session.commit()
        flash(u'删除成功')
        return  redirect(next or url_for('home.ceshihuanjing'))
class EditEventViews(MethodView):#编辑测试环境
    @login_required
    def get(self,id):
        if current_user.is_sper == True:
            projects=Project.query.filter_by(status=False).order_by('-id').all()
        else:
            projects=[]
            id=[]
            for i in current_user.quanxians:
                if  (i.projects in id)==False:
                    projects.append(i.projects)
                    id.append(i.projects)
        if len(projects)<=0:
            flash(u'你没有所属的项目，请在后台添加')
            return redirect(url_for('home.ceshihuanjing'))
        event=Interfacehuan.query.filter_by(id=id).first()
        return  render_template('edit/edit_events.html', enents=event, projects=projects)
    @login_required
    def post(self,id):
        data=request.get_json()
        project=Project.query.filter_by(project_name=data['work']).first()
        event = Interfacehuan.query.filter_by(id=id).first()
        event.url=data['url']
        event.desc=data['desc']
        event.database=data['datebase']
        event.databaseuser=data['datebaseuser']
        event.datebasepassword  =data['datebasepassword']
        event.project=project.id
        event.make_user=current_user.id
        try:
            db.session.commit()
            return  jsonify({'msg':'编辑成功','code':200})
        except Exception as e :
            db.session.rollback()
            return  jsonify({'msg':'编辑失败！原因是:%s'%e,'code':321,'data':''})
@app.route('/gettest',methods=['POST'])
@login_required
def gettest():#ajax获取项目的测试用例
    projec=(request.get_data('project')).decode('utf-8')
    if not projec:
        return []
    proje=Project.query.filter_by(project_name=str(projec)).first()
    if not proje:
        return  []
    testyong=InterfaceTest.query.filter_by(projects_id=proje.id).all()
    testyong_list=[]
    for i in testyong:
        testyong_list.append({'name':i.Interface_name,'id':i.id})
    return   jsonify({'data':testyong_list})
@app.route('/getprojects',methods=['GET','POST'])
@login_required
def getprojects():
    id = request.get_data('id')
    if not id:
        return jsonify({'msg':'没有发送数据','code':108})
    peoject=InterfaceTest.query.filter_by(id=int(id)).first()
    result=peoject.projects
    testhuanjing=Interfacehuan.query.filter_by(project=result.project_name).all()
    if len(testhuanjing)<=0:
        return jsonify({'msg': '没有找到测试环境','code':107,'data':str(result)})
    url_list=[]
    for huanjing in testhuanjing:
        url_list.append(huanjing.url)
    if not  peoject:
        return jsonify({'data':'数据库找不到项目','code':109})
    return  jsonify({'data':str(result),'huanjing':url_list,'code':200})
@app.route('/getyongli',methods=['GET','POST'])
def getyongli():
    id = request.get_data('id')
    project=id.decode('utf-8')
    if not project:
        return jsonify({'msg':'没有发送数据','code':108})
    peoject = Project.query.filter_by(project_name=project).first()
    if not  peoject:
        return jsonify({'msg': '数据库找不到项目', 'code': 109})
    tesatcaelist=InterfaceTest.query.filter_by(projects_id=peoject.id,status=False).all()
    caselit=[]
    for i in tesatcaelist:
        caselit.append(i.id)
    return  jsonify({'code':200,'msg':'成功','data':(caselit)})