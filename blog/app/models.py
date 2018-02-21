from datetime import datetime
from hashlib import md5
from app import app, db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
#from jwt import encode, decode

followers = db.Table(
	'followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

voters = db.Table(
	'voters',
	db.Column('voter_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('voted_id', db.Integer, db.ForeignKey('post.id'))
)

comments = db.Table(
	'comments',
	db.Column('commenter_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('commented_id', db.Integer, db.ForeignKey('post.id'))
)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)
	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
	voted = db.relationship(
		'Post', secondary=voters, lazy='dynamic')
	commented = db.relationship('Comment', secondary=comments, lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)
	
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'.format(digest=digest, size=size)
	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(followers.c.followed_id == user.id).count()>0
	def followed_posts(self):
		followed = Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
			followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Post.timestamp.desc())
	
	def vote(self, post):
		if not self.is_voting(post):
			self.voted.append(post)
	
	def unvote(self, post):
		if self.is_voting(post):
			self.voted.remove(post)
	
	def is_voting(self, post):
		return self.voted.filter(voters.c.voted_id == post.id).count()>0



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	voter = db.relationship('User', secondary=voters, lazy='dynamic')
	commenter = db.relationship('Comment', secondary=comments, lazy='dynamic')

	def _comments(self):
		comment = Comment.query.all()
		return followed.order_by(Post.timestamp.desc())

	def __repr__(self):
		return '<Post {}>'.format(self.body)

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(200))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Message {}>'.format(self.body)

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True)
	disabled = db.Column(db.Boolean)

	def __repr__(self):
		return '<Comment {}>'.format(self.body)


