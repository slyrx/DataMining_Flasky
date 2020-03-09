from flask import render_template, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import Permission, Role, User, Post, Report
from ..decorators import admin_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if not current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@main.route('/detail/<detailname>')
def detail(detailname):
    up_page = Report()
    result = []
    if detailname == "电子商务网站用户行为分析及服务推荐":
        result.append("LDA")
        result.append("语义网络")
        result.append("情感分析")
    elif detailname == "财政收入影响因素分析及预测模型":
        result.append("lda")
        result.append("语义网络")
        result.append("情感分析")
    elif detailname == "电力窃漏电用户自动识别":
        result.append("Cart 树")
        result.append("LM 神经网络")


    up_page.project_name = detailname
    up_page.models = result
    return render_template('analy_detail.html', detail=up_page)

@main.route('/report/<projectname>/<reportname>')
def report(projectname, reportname):
    result = None
    image_names = None
    import pandas as pd
    if projectname == "电子商务网站用户行为分析及服务推荐":

        from gensim import corpora, models
        posfile = '/Users/slyrx/Downloads/阿情感分析/comment_jd_cut.txt'
        stoplist = '/Users/slyrx/Downloads/Python数据分析与挖掘实战/chapter15/test/data/stoplist.txt'

        pos = pd.read_csv(posfile, encoding='utf-8', header=None)
        stop = pd.read_csv(stoplist, encoding='utf-8', header=None, sep='tipdm')

        stop = [' ', ''] + list(stop[0])

        pos[1] = pos[0].apply(lambda s: s.split(' '))
        pos[2] = pos[1].apply(lambda x: [i for i in x if i not in stop])

        pos_dict = corpora.Dictionary(pos[2])
        pos_corpus = [pos_dict.doc2bow(i) for i in pos[2]]
        pos_lda = models.LdaModel(pos_corpus, num_topics=3, id2word=pos_dict)
        result = pos_lda.print_topic(1)
    elif projectname == "电力窃漏电用户自动识别":
        if reportname == "Cart 树":
            from random import shuffle
            datafile = '/Users/slyrx/Downloads/Python数据分析与挖掘实战/chapter6/demo/data/model.xls'  # 数据名
            data = pd.read_excel(datafile)  # 读取数据，数据的前三列是特征，第四列是标签
            data = data.as_matrix()  # 将表格转换为矩阵
            shuffle(data)  # 随机打乱数据

            p = 0.8  # 设置训练数据比例
            train = data[:int(len(data) * p), :]  # 前80%为训练集
            test = data[int(len(data) * p):, :]  # 后20%为测试集

            from sklearn.tree import DecisionTreeClassifier
            tree = DecisionTreeClassifier()  # 建立决策树模型
            tree.fit(train[:, :3], train[:, 3])  # 训练

            result = str(tree.predict(train[:,:3])) + '****' + str(train[:, 3])
            image_names = ['cm_cart.png', 'roc_cart.png']
        elif reportname == "LM 神经网络":
            image_names = ['cm_lm.png', 'roc_lm.png']
            pass



    return render_template('analy_report.html', report=result, model_name = reportname, imagename=image_names)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
