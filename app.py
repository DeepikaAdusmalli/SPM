from flask import Flask,request,redirect,render_template,url_for,flash,session,send_file
from flask_mysqldb import MySQL
from flask_session import Session
from otp import genotp
from cmail import sendmail
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
from io import BytesIO
app=Flask(__name__)
app.secret_key='*feojf68958#'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='SPM'
Session(app)
mysql=MySQL(app)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/registration',methods=['GET','POST'])
def register():
    if request.method=='POST':
        rollno=request.form['rollno']
        name=request.form['name']
        group=request.form['group']
        password=request.form['password']
        code=request.form['Ccode']
        email=request.form['email']
        #define college code
        Ccode='sdmsmkpbsc$#123'
        if Ccode==code:
            cursor=mysql.connection.cursor()
            cursor.execute('select rollno from students')
            data=cursor.fetchall()
            cursor.execute('select email from students')
            edata=cursor.fetchall()
            #print(data)
            if(rollno,) in data:
                flash('user already exist')
                return render_template('register.html')
            if(email,) in edata:
                flash('email id already exist')
                return render_template('register.html')
            cursor.close()
            otp=genotp()
            subject='Thanks for registering to the application'
            body=f'Us this otp to register{otp}'
            sendmail(email,subject,body)
            return render_template('otp.html',otp=otp,rollno=rollno,name=name,group=group,password=password,email=email)
        else:
            flash('Invalid Code')
            return render_template('register.html')
    return render_template('register.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        rollno=request.form['id']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from students where rollno=%s and password=%s',[rollno,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('invalid rollno or password')
            return render_template('login.html')
        else:
            session['user']=rollno
            return redirect(url_for('home'))
    return render_template('login.html')
@app.route('/Studenthome')
def home():
    if session.get('user'):
        return render_template('home.html')
    else:
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('index'))
    else:
        flash('already logged out!')
        return redirect(url_for('login'))
@app.route('/otp/<otp>/<rollno>/<name>/<group>/<password>/<email>',methods=['GET','POST'])
def otp(otp,rollno,name,group,password,email):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            lst=[rollno,name,group,password,email]
            query='insert into students values(%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,rollno=rollno,name=name,group=group,password=password,email=email)
@app.route('/noteshome')
def noteshome():
    if session.get('user'):
        rollno=session.get('user')
        cursor=mysql.connection.cursor()
        cursor.execute('select * from notes where rollno=%s',[rollno])
        notes_data=cursor.fetchall()
        print(notes_data)
        return render_template('addnotetable.html',data=notes_data)
        return render_template('addnotetable.html')
    else:
        return redirect(url_for('login'))
@app.route('/addnotes',methods=['GET','POST'])
def addnotes():
    if session.get('user'):
        if request.method=='POST':
            tittle=request.form['Tittle']
            content=request.form['content']
            cursor=mysql.connection.cursor()
            rollno=session.get('user')
            cursor.execute('insert into notes(rollno,tittle,content) values(%s,%s,%s)',[rollno,tittle,content])
            mysql.connection.commit()
            cursor.close()
            flash(f'{tittle} added successfully')
            return redirect(url_for('noteshome'))
        return render_template('notes.html')
    else:
        return redirect(url_for('login'))
@app.route('/viewnotes/<nid>')
def viewnotes(nid):
    cursor=mysql.connection.cursor()
    cursor.execute('select tittle,content from notes where nid=%s',[nid])
    data=cursor.fetchone()
    return render_template('notesview.html',data=data)
@app.route('/updatenotes/<nid>',methods=['GET','POST'])
def updatenotes(nid):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select tittle,content from notes where nid=%s',[nid])
        data=cursor.fetchone()
        if request.method=='POST':
            tittle=request.form['tittle']
            content=request.form['content']
            cursor=mysql.connection.cursor()
            cursor.execute('update notes set tittle=%s,content=%s where nid=%s',[tittle,content,nid])
            mysql.connection.commit()
            cursor.close()
            flash('Notes update successfully')
            return redirect(url_for('login'))
        return render_template('updatenotes.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/deletenotes/<nid>')
def deletenotes(nid):
    cursor=mysql.connection.cursor()
    cursor.execute('delete from notes where nid=%s',[nid])
    mysql.connection.commit()
    cursor.close()
    flash('notes deleted successfully')
    return redirect(url_for('noteshome'))
@app.route('/fileshome')
def fileshome():
    if session.get('user'):
        rollno=session.get('user')
        cursor=mysql.connection.cursor()
        cursor.execute('select fid,filename,date from files where rollno=%s',[rollno])
        data=cursor.fetchall()
        cursor.close()
        return render_template('fileuploadtable.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/filehandling',methods=['POST'])
def filehandling():
    file=request.files['file']
    filename=file.filename
    bin_file=file.read()
    rollno=session.get('user')
    cursor=mysql.connection.cursor()
    cursor.execute('insert into files(rollno,filename,filedata) values(%s,%s,%s)',[rollno,filename,bin_file])
    mysql.connection.commit()
    cursor.close()
    flash(f'{filename}upload successfully')
    return redirect(url_for('fileshome'))
@app.route('/viewfile/<fid>')
def viewfile(fid):
    if session.get('user'):
            cursor=mysql.connection.cursor()
            cursor.execute('select filename,filedata from files where fid=%s',[fid])
            data=cursor.fetchone()
            cursor.close()
            filename=data[0]
            bin_file=data[1]
            byte_data=BytesIO(bin_file)
            return send_file(byte_data,download_name=filename)
    else:
        return redirect(url_for('login'))
@app.route('/filedelete/<fid>')
def filedelete(fid):
    cursor=mysql.connection.cursor()
    cursor.execute('delete from files where fid=%s',[fid])
    mysql.connection.commit()
    cursor.close()
    flash('File deleted successfully')
    return redirect(url_for('fileshome'))
@app.route('/forgetpassword',methods=['GET','POST'])
def forget():
    if request.method=='POST':
        rollno=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('select rollno from students')
        data=cursor.fetchall()
        if(rollno,) in data:
            cursor.execute('select email from students where rollno=%s',[rollno])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the password using-{request.host+url_for("createpassword",token=token(rollno,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'invalid user id'
    return render_template('forget.html')
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
        try:
            s=Serializer(app.config['SECRET_KEY'])
            rollno=s.loads(token)['user']
            if request.method=='POST':
                npass=request.form['npassword']
                cpass=request.form['cpassword']
                if npass==opass:
                    cursor=mysql.connection.cursor()
                    cursor.execute('update students set password=%s where rollno=%s',[npass,rollno])
                    mysql.connection.commit()
                    return 'password reset successful'
                else:
                    return 'password mismatched'
            return render_template('newpassword.html')
        except:
            return 'Link expired!Start again'
app.run(use_reloader=True,debug=True)

