from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import datetime



# Configuration for the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_database.sqlite3'
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()




# Models for the app 
class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)
    email = db.Column(db.String, unique = True, nullable = False)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String)
    password = db.Column(db.String, nullable = False)
    dob = db.Column(db.String, nullable = False)

class Posts(db.Model):
    __tablename__='posts'
    post_id = db.Column(db.Integer, nullable = False, autoincrement = True, unique= True, primary_key = True)
    title = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    attachment = db.Column(db.String)
    username = db.Column(db.String, db.ForeignKey("users.username"),nullable=False)
    datetime = db.Column(db.String)


class Follow(db.Model):
    __tablename__='follow'
    follow_id=db.Column(db.Integer, nullable = False, autoincrement = True, unique= True, primary_key = True)
    following = db.Column(db.String, nullable = False)
    follower = db.Column(db.String, nullable = False)


# Controller for Login page
@app.route('/',methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username=request.form["username"]
        password=request.form["password"]
        user = Users.query.filter_by(username=username,password=password).first()
        if user is None:
            return render_template("login_error.html") 
        else:
            return redirect("/"+username+"/home")
            # post=Posts.query.all()
            # if len(post)==0:
            #     return render_template("home_empty.html",users=user)
            # return render_template("home.html",users=user,posts=post)




# Controller for Registration Page
@app.route('/registration',methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    else:
        user=Users(first_name=request.form["fname"],last_name=request.form["lname"],username=request.form["uname"],password=request.form["pass"],email=request.form["email"],dob=request.form["dob"])
        db.session.add(user)
        db.session.commit()
        return redirect("/")




# Controller for Home page
@app.route('/<username>/home',methods=['GET'])
def home(username):
    if request.method == "GET":
        user = Users.query.filter_by(username=username).first()
        post=Posts.query.all()
        follow=[]
        follows=Follow.query.filter_by(follower=username).all()
        for i in follows:
            follow+=[i.following]
        if len(post)==0:
            return render_template("home_empty.html",users=user)
        else : 
            return render_template("home.html",users=user,posts=post,follow=follow)





# Controller for Summary
@app.route('/<username>/my_profile',methods=['GET','POST'])
def summary(username):
    if request.method=='GET':
        user = Users.query.filter_by(username=username).first()
        posts = Posts.query.filter_by(username=username).all()
        total_posts=len(posts)
        followers = Follow.query.filter_by(follower=username).all()
        following = Follow.query.filter_by(following=username).all()
        total_followers=len(followers)
        total_following=len(following)
        return render_template("summary.html",users=user,total_posts=total_posts,posts=posts,total_followers=total_followers,total_following=total_following)




# Controller for Search bar
@app.route('/<username>/search',methods=['GET','POST'])
def search(username):
    if request.method=='GET':
        user = Users.query.filter_by(username=username).first()
        return render_template("search.html",users=user)
    else:
        user = Users.query.filter_by(username=username).first()
        search=request.form.get("search")
        result=Users.query.filter(or_(Users.username.like(search),Users.first_name.like(search),Users.last_name.like(search))).all()
        if user in result:
            result.remove(user)
        if len(result)==0:
            search=search.capitalize()
            return render_template("no_match.html",users=user,search=search)
        results,follow=[],[]
        for i in result:
            results+=[i.username]
        follows=Follow.query.filter_by(follower=username).all()
        for i in follows:
            follow+=[i.following]
        return render_template("search_results.html",users=user,results=results,follow=follow)



# Controller for New Post
@app.route('/<username>/new_post',methods=['GET','POST'])
def new_post(username):
    if request.method=='GET':
        user = Users.query.filter_by(username=username).first()
        return render_template("new_post.html",users=user)
    if request.method=='POST':
        user = Users.query.filter_by(username=username).first()
        post=Posts(title=request.form.get("pname"),description=request.form.get("pdescription"),username=username,datetime=datetime.datetime.now())
        db.session.add(post)
        db.session.commit()
        return redirect("/"+username+"/my_profile")




# Controller for seeing other user profiles
@app.route('/<username>/profile/<other_username>',methods=['GET','POST'])
def other_profile(username,other_username):
    if request.method=='GET':
        user=Users.query.filter_by(username=username).first()
        posts = Posts.query.filter_by(username=other_username).all()
        total_posts=len(posts)
        followers = Follow.query.filter_by(follower=other_username).all()
        following = Follow.query.filter_by(following=other_username).all()
        total_followers=len(followers)
        total_following=len(following)
        return render_template("other_summary.html",users=user,total_posts=total_posts,posts=posts,other_user_name=other_username,total_followers=total_followers,total_following=total_following)




# Controller for Deleting a post
@app.route('/<username>/delete/<post_id>',methods=['GET','POST'])
def delete(username,post_id):
    if request.method=='GET':
        post=Posts.query.filter_by(post_id=post_id).first()
        db.session.delete(post)
        db.session.commit()
        return redirect("/"+username+"/my_profile")




# Controller for Updating a post
@app.route('/<username>/update/<post_id>',methods=['GET','POST'])
def update(username,post_id):
    if request.method=='GET':
        user = Users.query.filter_by(username=username).first()
        post=Posts.query.filter_by(post_id=post_id).first()
        return render_template("update.html",users=user,post=post)
    elif request.method=='POST':
        post=Posts.query.filter_by(post_id=post_id).first()
        if request.form.get("pname")!='':
            post.title=request.form.get("pname")
        if request.form.get("pdescription")!='':
            post.description=request.form.get("pdescription")
        post.datetime=datetime.datetime.now()
        db.session.commit()
        return redirect("/"+username+"/my_profile")




# Controller for follow
@app.route('/<follower>/follow/<following>',methods=['GET','POST'])
def follow(following,follower):
    if request.method=='GET':
        follow=Follow(following=following,follower=follower)
        db.session.add(follow)
        db.session.commit()
        return redirect('/'+follower+'/my_profile')




# Controller for unfollow
@app.route('/<follower>/unfollow/<following>',methods=['GET','POST'])
def unfollow(following,follower):
    if request.method=='GET':
        follow=Follow.query.filter_by(following=following,follower=follower).first()
        db.session.delete(follow)
        db.session.commit()
        return redirect('/'+follower+'/my_profile')




if __name__ == "__main__":
    app.debug=True
    app.run()
