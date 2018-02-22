from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, MessageForm, CommentForm
from app.models import User, Post, Message, Comment
from datetime import datetime
from werkzeug import secure_filename
import os

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in app.config['ALLOWED_EXTENSIONS']

def allowed_avatar(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in app.config['ALLOWED_AVATAR_EXTENSIONS']

@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post is now live!')
		return redirect(url_for('index'))
	page = request.args.get('page', 1, type=int)
	posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html', title='Home',form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username = username).first_or_404()
	page = request.args.get('page', 1, type=int)
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(
			page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
	prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
	return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
	post = Post.query.get_or_404(id)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body = form.message.data, post=post, author=current_user)
		db.session.add(comment)
		db.session.commit()
		flash('Your comment has been published.')
		return redirect(url_for('post',id=post.id))
	page = request.args.get('page', 1, type=int)
	comments = post._comments().paginate(page, app.config['COMMENTS_PER_PAGE'], False)
	next_url = url_for('post', id=id, page=comments.next_num) if comments.has_next else None
	prev_url = url_for('post', id=id, page=comments.prev_num) if comments.has_prev else None
	return render_template('_post.html', post=post, form=form, comments=comments.items, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		avatar = request.files['avatar']
		if avatar:
			if not allowed_avatar(avatar.filename):
				flash('Invalid file type! Only .jpg, .jpeg, .png, .gif are allowed.')
				return redirect(url_for('edit_profile'))
		filename = secure_filename(avatar.filename)
		avatar.save('{}/{}/{}_{}'.format(os.path.join(os.path.dirname(os.path.realpath(__file__))), app.config['UPLOAD_AVATAR_FOLDER'], current_user.username, filename))
		current_user.avatar = '../{}/{}_{}'.format(app.config['UPLOAD_AVATAR_FOLDER'], current_user.username, filename)
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('user', username = current_user.username))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
	post = Post.query.get(id)
	if post is None:
		flash('Post not found.')
		return redirect(url_for('index'))
	if post.author.id != current_user.id:
		flash('You cannot delete this post.')
		return redirect(url_for('index'))
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted.')
	return redirect(url_for('index'))

@app.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot follow yourself!')
		return redirect(url_for('user', username=username))
	current_user.follow(user)
	db.session.commit()
	flash('You are following {}!'.format(username))
	return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot unfollow yourself!')
		return redirect(url_for('user', username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You are not following {}!'.format(username))
	return redirect(url_for('user',username=username))



@app.route('/vote/<int:id>')
@login_required
def vote(id):
	post = Post.query.get(id)
	if post is None:
		flash('Post not found.')
		return redirect(url_for('index'))
	current_user.vote(post)
	db.session.commit()
	flash('You have successfully voted for this blog!')
	return redirect(url_for('index'))
	 
@app.route('/unvote/<int:id>')
@login_required
def unvote(id):
	post = Post.query.get(id)
	if post is None:
		flash('Post not found.')
		return redirect(url_for('index'))
	if not post.voter.count()>0:
		flash('No one has voted for this blog.')
		return redirect(url_for('index'))
	current_user.unvote(post)
	db.session.commit()
	flash('You have successfully unvoted for this blog!')
	return redirect(url_for('index'))

@app.route('/leave_message', methods=['GET', 'POST'])
@login_required
def leave_message():
	form = MessageForm()
	if form.validate_on_submit():
		message = Message(body=form.message.data, user_id = current_user.id)
		db.session.add(message)
		db.session.commit()
		flash('You successfully leave a message to us!')
		return redirect(url_for('leave_message'))
	return render_template('leave_message.html', title='Leave a Message',form=form)

@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(os.path.dirname(os.path.realpath(__file__)), app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('uploaded_file', filename=filename))
		return '<p>The file''s type is invalid.</p>'
	return '''
	<!DOCTYPE html>
	<title>Change new icon</title>
	<h1>Upload new</h1>
	<form action = "" method = "post" enctype=multipart/form-data>
		<input type = "file" name = file>
		<input type = "submit" value = Upload>
	</form>
	'''

@app.route('/uploaded_file/<filename>')
@login_required
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
