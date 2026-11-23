from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, datetime, os, random
app = Flask(__name__)
app.secret_key = 'sandhu123'
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')
def db():
    con = sqlite3.connect('academy.db')
    con.execute('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, category TEXT, title TEXT, duration TEXT, fee TEXT, detail TEXT, video_url TEXT, image TEXT, page_no TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS teachers (id INTEGER PRIMARY KEY, name TEXT, subject TEXT, exp TEXT, image TEXT, detail TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, username TEXT, password TEXT, role TEXT, class TEXT, fee TEXT, marks TEXT, meet_link TEXT, pic TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS discount_apps (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, course TEXT, reason TEXT, status TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, student_name TEXT, marks TEXT, image TEXT, video_url TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, name TEXT, msg TEXT, screenshot TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, student_name TEXT, phone TEXT, course TEXT, amount TEXT, trxid TEXT, screenshot TEXT, status TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS ai_chats (id INTEGER PRIMARY KEY, q TEXT, a TEXT)')
    if not con.execute("SELECT * FROM users WHERE username='fatima_admin'").fetchone():
        con.execute("INSERT INTO users (name,username,password,role) VALUES ('Fatima Sandhu','fatima_admin','Fatima@0311','admin')")
    con.commit(); return con
@app.route('/')
def home(): return render_template('index.html')
@app.route('/courses')
def courses():
    page = request.args.get('page','1')
    con=db()
    if page=='1' or not page: data=con.execute('SELECT * FROM courses').fetchall()
    else: data=con.execute('SELECT * FROM courses WHERE page_no=?',(page,)).fetchall()
    con.close(); return render_template('courses.html', courses=data)
@app.route('/course/<cat>')
def course_cat(cat):
    con=db(); data=con.execute('SELECT * FROM courses WHERE category=?',(cat,)).fetchall(); con.close(); return render_template('course_detail.html', cat=cat, courses=data)
@app.route('/teachers')
def teachers():
    con=db(); data=con.execute('SELECT * FROM teachers').fetchall(); con.close(); return render_template('teachers.html', teachers=data)
@app.route('/discount', methods=['GET','POST'])
def discount():
    if request.method=='POST':
        con=db(); con.execute('INSERT INTO discount_apps (name,phone,course,reason,status) VALUES (?,?,?,?,\'Pending\')',(request.form['name'],request.form['phone'],request.form['course'],request.form.get('reason',''))); con.commit(); con.close(); return render_template('discount_success.html')
    return render_template('discount.html')
@app.route('/internship')
def internship(): return render_template('internship.html')
@app.route('/payment', methods=['GET','POST'])
def payment():
    if request.method=='POST':
        f=request.files.get('screenshot'); fname=""
        if f and f.filename: fname=f.filename; f.save("static/uploads/"+fname)
        con=db(); con.execute('INSERT INTO payments (student_name,phone,course,amount,trxid,screenshot,status) VALUES (?,?,?,?,?,?,?)',(request.form['student_name'],request.form['phone'],request.form.get('course',''),request.form['amount'],request.form['trxid'],fname,'Pending')); con.commit(); con.close()
        return "Payment Submit Ho Gayi! Admin Approve Karegi. <a href='/'>Home</a>"
    return render_template('payment.html')
@app.route('/contact', methods=['GET','POST'])
def contact():
    today = datetime.date.today().strftime("%A, %d %B %Y")
    if request.method=='POST':
        f = request.files.get('screenshot'); fname=""
        if f and f.filename: fname=f.filename; f.save("static/uploads/"+fname)
        con=db(); con.execute('INSERT INTO contacts (name,msg,screenshot) VALUES (?,?,?)',(request.form['name'],request.form['msg'],fname)); con.commit(); con.close()
        return redirect("https://wa.me/923116402301?text=Assalam%20o%20Alaikum%20Mujhe%20more%20info%20chahiye")
    return render_template('contact.html', today=today)
@app.route('/results')
def results():
    con=db(); data=con.execute('SELECT * FROM results').fetchall(); con.close(); return render_template('results.html', results=data)
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        con=db(); u=con.execute('SELECT * FROM users WHERE username=? AND password=?',(request.form['user'],request.form['pass'])).fetchone(); con.close()
        if u:
            session['user']=u[2]; session['role']=u[4]; session['name']=u[1]
            if u[4]=='admin': return redirect('/admin')
            elif u[4]=='teacher': return redirect('/teacher_dashboard')
            else: return redirect('/student_dashboard')
        return "Ghalat Username ya Password!"
    return render_template('login.html')
@app.route('/admin')
def admin():
    if session.get('role')!='admin': return redirect('/login')
    con=db()
    courses=con.execute('SELECT * FROM courses').fetchall()
    teachers=con.execute('SELECT * FROM teachers').fetchall()
    students=con.execute("SELECT * FROM users WHERE role='student'").fetchall()
    teacher_users=con.execute("SELECT * FROM users WHERE role='teacher'").fetchall()
    apps=con.execute('SELECT * FROM discount_apps').fetchall()
    results=con.execute('SELECT * FROM results').fetchall()
    contacts=con.execute('SELECT * FROM contacts').fetchall()
    payments=con.execute('SELECT * FROM payments').fetchall()
    con.close()
    return render_template('admin.html', courses=courses, teachers=teachers, students=students, teacher_users=teacher_users, apps=apps, results=results, contacts=contacts, payments=payments, name=session.get('name'))
@app.route('/change_bg', methods=['POST'])
def change_bg():
    f=request.files.get('bg')
    if f and f.filename: f.save("static/bg.jpg")
    return redirect('/admin')
@app.route('/change_bg_remove', methods=['POST'])
def change_bg_remove():
    if os.path.exists("static/bg.jpg"): os.remove("static/bg.jpg")
    return redirect('/admin')
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role')!='student': return redirect('/login')
    con=db(); me=con.execute('SELECT * FROM users WHERE username=?',(session['user'],)).fetchone(); con.close(); return render_template('student_dashboard.html', me=me)
@app.route('/student_pic', methods=['POST'])
def student_pic():
    if session.get('role')!='student': return redirect('/login')
    f=request.files.get('pic')
    if f and f.filename:
        fname=f.filename; f.save("static/uploads/"+fname)
        con=db(); con.execute("UPDATE users SET pic=? WHERE username=?", (fname, session.get('user'))); con.commit(); con.close()
    return redirect('/student_dashboard')
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('role')!='teacher': return redirect('/login')
    con=db(); students=con.execute("SELECT * FROM users WHERE role='student'").fetchall(); courses=con.execute('SELECT * FROM courses').fetchall(); con.close(); return render_template('teacher_dashboard.html', students=students, courses=courses, name=session.get('name'))
@app.route('/teacher_update_link', methods=['POST'])
def teacher_update_link():
    con=db(); con.execute("UPDATE users SET meet_link=? WHERE role='student'", (request.form['meet_link']+" | Class: "+request.form['class_name']+" | Time: "+request.form['time']+" | Duration: "+request.form['duration'],)); con.commit(); con.close(); return "Link Bachon Ko Bhej Diya Gaya! <a href='/teacher_dashboard'>Wapis Jao</a>"
@app.route('/verify_discount/<int:id>/<status>')
def verify_discount(id, status):
    con=db(); con.execute("UPDATE discount_apps SET status=? WHERE id=?", (status, id)); con.commit(); con.close(); return redirect('/admin')
@app.route('/approve_payment/<int:id>/<status>')
def approve_payment(id, status):
    con=db(); con.execute("UPDATE payments SET status=? WHERE id=?", (status, id)); con.commit(); con.close(); return redirect('/admin')
# --- AI - GOOGLE JAISA EXPERT ---
@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    msg_raw = request.form.get('msg','')
    msg = msg_raw.lower().strip()
    ans = ""
    dictionary = {
        'apple':'Apple means Seb 🍎. Example: I eat an apple.',
        'book':'Book means Kitaab 📚. Example: This is my book.',
        'school':'School means School 🏫. Example: I go to school.',
        'teacher':'Teacher means Ustad 👩‍🏫. Example: My teacher is kind.',
        'water':'Water means Pani 💧. Example: Drink water.',
        'happy':'Happy means Khush 😊. Example: I am happy today.',
        'friend':'Friend means Dost 🤝. Example: Ali is my friend.',
        'mother':'Mother means Ammi ❤️','father':'Father means Abu ❤️',
        'cat':'Cat means Billi 🐱','dog':'Dog means Kutta 🐶','sun':'Sun means Suraj ☀️',
        'moon':'Moon means Chand 🌙','love':'Love means Mohabbat ❤️','pen':'Pen means Qalam ✏️',
        'home':'Home means Ghar 🏠','girl':'Girl means Larki 👧','boy':'Boy means Larka 👦',
        'eat':'Eat means Khana 🍽️','drink':'Drink means Peena 🥤','sleep':'Sleep means Sona 😴',
        'read':'Read means Parhna 📖','write':'Write means Likhna ✍️','run':'Run means Dourna 🏃',
        'chair':'Chair means Kursi 🪑','table':'Table means Meez','door':'Door means Darwaza 🚪',
        'car':'Car means Gari 🚗','bird':'Bird means Parinda 🐦','fish':'Fish means Machli 🐟',
    }
    for w, m in dictionary.items():
        if w in msg and ('matlab' in msg or 'means' in msg or 'meaning' in msg or w==msg):
            ans = m; break
    if not ans:
        if 'tense' in msg or 'present' in msg or 'past' in msg or 'future' in msg:
            ans = "📖 TENSES:\n1. Present Simple: I go to school. (Roz ka kaam)\n2. Past Simple: I went to school. (Kal ka kaam)\n3. Future Simple: I will go to school. (Kal ka plan)\nExample: She plays / She played / She will play."
        elif 'jazzcash' in msg or 'jazz cash' in msg or 'payment' in msg or 'fee' in msg or 'paisa' in msg:
            ans = "💰 JAZZCASH GUIDE:\n1. JazzCash App kholo\n2. Send Money dabao\n3. Number: 03116402301\n4. Name: Fatima Sandhu\n5. Amount: 1000\n6. Send karo, Trx ID copy karo\n7. Is website pe Payment page pe ja ke Trx ID likh ke Submit karo. Ho gaya! ✅"
        elif 'offer' in msg: ans = "🎁 OFFER! 2 Din FREE Trial + Orphan ko Discount + 1st Month me 20% Off! WhatsApp 03116402301"
        elif 'admission' in msg or 'dakhla' in msg: ans = "Admission ke liye WhatsApp 03116402301 pe naam + class bhejo. Fatima Sandhu khud jawab dengi. Welcome! 🎉"
        elif 'teacher' in msg: ans = "Hamare paas 8 Years Experience wali Female Teachers hain. Ghar beth ke bhi parh sakti ho."
        elif 'timing' in msg or 'time' in msg or 'kab' in msg: ans = "Classes subah 9 se raat 9 tak hoti hain. Tum apna time bata do."
        elif 'coding' in msg or 'python' in msg: ans = "Coding me C, C++, Python, Java, HTML, CSS, Website banana aur AI Prompt sikhate hain. Bilkul asaan tareeke se!"
        elif 'english' in msg: ans = "English me Bolna + Likhna dono hain. Page 1: Grammar, Page 2: Bolna, Page 3: Likhna."
        elif 'maths' in msg or 'math' in msg: ans = "Maths me hum asaan tareeka sikhate hain. Example: 5 + 5 = 10."
        elif 'salam' in msg or 'hello' in msg or 'hi' in msg: ans = "Walaikum Assalam! 😊 Sandhu Academy me welcome. Fee, Tenses, JazzCash, Dictionary - kuch bhi pucho!"
        elif 'tension' in msg or 'mushkil' in msg or 'dar' in msg: ans = "Tension na lo! 😊 Yahan sab asaan tareeke se sikhate hain. Teacher dobara samjhayegi."
        elif 'thank' in msg or 'shukriya' in msg: ans = "Welcome! ❤️ Tum khush ho to hum khush hain."
        elif 'tum kaun' in msg or 'tumhara naam' in msg: ans = "Main Sandhu Academy ki AI hun. Fatima Sandhu ne mujhe banaya hai."
        elif 'kahan' in msg or 'gujranwala' in msg: ans = "Hamari Academy Gujranwala me hai, per Online poore Pakistan me parhate hain."
        else: ans = f"'{msg_raw}' - Iska jawab: Fee Rs.1000 hai, Classes subah 9 se raat 9 tak hain, Teacher 8 Years Experience wali hain. Agar Tense, Dictionary, JazzCash ke bare me pooch rahe ho to dobara likho, jaise 'Tenses kya hain?' ya 'JazzCash kaise bhejun?'"
    try:
        con=db(); con.execute("INSERT INTO ai_chats (q,a) VALUES (?,?)",(msg_raw, ans)); con.commit(); con.close()
    except: pass
    return ans
@app.route('/ai_chats')
def ai_chats():
    if session.get('role')!='admin': return redirect('/login')
    con=db(); data=con.execute('SELECT * FROM ai_chats ORDER BY id DESC LIMIT 100').fetchall(); con.close()
    html="<h2 style='text-align:center'>🤖 Bachon Ki AI Chat</h2><div style='max-width:800px;margin:auto'>"
    for d in data: html+=f"<div style='background:white;padding:15px;border-radius:15px;margin:10px'><b>Bacha:</b> {d[1]}<br><b>AI:</b> {d[2]}</div>"
    html+="</div><p style='text-align:center'><a href='/admin'>Wapis Admin</a></p>"
    return html
@app.route('/add_course', methods=['POST'])
def add_course():
    con=db(); img = request.files.get('image'); img_name=""
    if img and img.filename: img_name=img.filename; img.save("static/uploads/"+img_name)
    con.execute('INSERT INTO courses (category,title,duration,fee,detail,video_url,image,page_no) VALUES (?,?,?,?,?,?,?,?)',(request.form['category'],request.form['title'],request.form['duration'],request.form['fee'],request.form['detail'],request.form.get('video_url',''),img_name,request.form.get('page_no','1'))); con.commit(); con.close(); return redirect('/admin')
@app.route('/delete_course/<int:id>')
def delete_course(id):
    con=db(); con.execute('DELETE FROM courses WHERE id=?',(id,)); con.commit(); con.close(); return redirect('/admin')
@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    con=db(); img=request.files.get('image'); img_name=""
    if img and img.filename: img_name=img.filename; img.save("static/uploads/"+img_name)
    con.execute('INSERT INTO teachers (name,subject,exp,image,detail) VALUES (?,?,?,?,?)',(request.form['name'],request.form['subject'],request.form['exp'],img_name,request.form.get('detail',''))); con.commit(); con.close(); return redirect('/admin')
@app.route('/delete_teacher/<int:id>')
def delete_teacher(id):
    con=db(); con.execute('DELETE FROM teachers WHERE id=?',(id,)); con.commit(); con.close(); return redirect('/admin')
@app.route('/add_teacher_user', methods=['POST'])
def add_teacher_user():
    con=db(); con.execute("INSERT INTO users (name,username,password,role) VALUES (?,?,?,'teacher')",(request.form['name'],request.form['username'],request.form['password'])); con.commit(); con.close(); return redirect('/admin')
@app.route('/add_student_user', methods=['POST'])
def add_student_user():
    con=db(); con.execute("INSERT INTO users (name,username,password,role,class,fee,marks,meet_link) VALUES (?,?,?,'student',?,?,?,?)",(request.form['name'],request.form['username'],request.form['password'],request.form['class'],request.form['fee'],request.form['marks'],request.form.get('meet_link',''))); con.commit(); con.close(); return redirect('/admin')
@app.route('/delete_student/<int:id>')
def delete_student(id):
    con=db(); con.execute('DELETE FROM users WHERE id=?',(id,)); con.commit(); con.close(); return redirect('/admin')
@app.route('/add_result', methods=['POST'])
def add_result():
    con=db(); img = request.files.get('image'); img_name=""
    if img and img.filename: img_name=img.filename; img.save("static/uploads/"+img_name)
    con.execute('INSERT INTO results (student_name,marks,image,video_url) VALUES (?,?,?,?)',(request.form['student_name'],request.form['marks'],img_name,request.form.get('video_url',''))); con.commit(); con.close(); return redirect('/admin')
@app.route('/logout')
def logout(): session.clear(); return redirect('/login')
if __name__=='__main__': app.run(debug=True)