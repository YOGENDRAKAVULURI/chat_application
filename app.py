import os
os.environ["EVENTLET_NO_GREENDNS"] = "yes"

import eventlet
eventlet.monkey_patch()

import bcrypt
from datetime import datetime
from flask import (Flask, flash, render_template, redirect, url_for,request, session, jsonify)
import uuid
from werkzeug.utils import secure_filename
from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room, emit
import mysql.connector
import os
from cmail import send_email       # you said you have these
from otp import userotp
from stoken import generate_token, verify_token
from urllib.parse import quote_plus  # add at the top if not present

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret")
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
# where to store uploaded avatars
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_IMAGE_EXTS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
online_users = set()

def allowed_image(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTS

# IMPORTANT: threading mode is safest on Windows/Python 3.13
socketio = SocketIO(app, manage_session=False, async_mode='gevent')

# ---------- DB helper: open a NEW connection per request/event ----------
def get_db():
    return mysql.connector.connect(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        port=int(os.environ.get("DB_PORT")),
        autocommit=True
    )


# ---------- Utilities ----------
def require_login_redirect():
    if session.get('email') is None:
        flash('please login first', 'registration')
        return False
    return True

# ---------- Pages ----------
@app.route('/')
def index():
    # You can point this to your login/registration or dashboard.
    if session.get('email'):
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/home')
def home():
    # your combined Register/Login template name; adjust if different
    return render_template('registration.html')

@app.route('/dashboard')
def dashboard():
    if not require_login_redirect():
        return redirect(url_for('home'))
    # Use dashboard.html as base; children will extend it.
    # It must define ONE block 'content' to be filled by child pages.
    return render_template('dashboard.html')

@app.route('/room_home')
def room_home():
    if not require_login_redirect():
        return redirect(url_for('home'))
    return render_template('room_home.html',
                           user_id=session.get('user_id'),
                           username=session.get('username'),
                           email=session.get('email'))

@app.route('/room')
def room():
    if not require_login_redirect():
        return redirect(url_for('home'))
    # room.html expects user_id to align "You" messages
    return render_template('room.html',
                           user_id=session.get('user_id'),
                           username=session.get('username'),
                           email=session.get('email'))

# ---------- Auth ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('Username')
        email = request.form.get('Email')
        password = request.form.get('Password')
        otp_code = userotp()

        db = get_db()
        cur = db.cursor(buffered=True)
        try:
            cur.execute("SELECT COUNT(*) FROM userdata WHERE email=%s", (email,))
            dup = cur.fetchone()[0]
            if dup:
                flash('email already registered', 'registration')
                return redirect(url_for('home'))

            # Send OTP email
            subject = "Your OTP for Signup"
            body = f"Hello {username},\nYour OTP for signup is {otp_code}.\nPlease do not share it with anyone."
            send_email(to=email, subject=subject, body=body)

            signed = generate_token({
                'username': username,
                'email': email,
                'password': password,
                'otp': otp_code
            })
            return redirect(url_for('otpverify', signed_userdata=signed))
        finally:
            cur.close()
            db.close()
    return render_template('registration.html')

@app.route('/otpverify/<signed_userdata>', methods=['GET', 'POST'])
def otpverify(signed_userdata):
    if request.method == 'POST':
        user_otp = ''.join([request.form.get(f'otp{i}') for i in range(1, 7)])
        try:
            de_data = verify_token(signed_userdata)
        except Exception:
            flash('could not verify otp', 'otpverify')
            return redirect(url_for('otpverify', signed_userdata=signed_userdata))

        if user_otp != de_data['otp']:
            flash('given otp was wrong', 'otpverify')
            return redirect(url_for('otpverify', signed_userdata=signed_userdata))

        # Store user
        db = get_db()
        cur = db.cursor(buffered=True)
        try:
            bytes_password = de_data['password'].encode('utf-8')
            hash_password = bcrypt.hashpw(bytes_password, bcrypt.gensalt()).decode('utf-8')
            cur.execute(
                "INSERT INTO userdata (username, email, password) VALUES (%s, %s, %s)",
                (de_data['username'], de_data['email'], hash_password)
            )
            db.commit()
            flash('successfully created account, please login', 'registration')
            return redirect(url_for('home'))
        except Exception:
            db.rollback()
            flash('could not store user data', 'otpverify')
            return redirect(url_for('otpverify', signed_userdata=signed_userdata))
        finally:
            cur.close()
            db.close()
    return render_template('otpverify.html', signed_userdata=signed_userdata)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('Email1')
    password = request.form.get('Password1')
    db = get_db()
    cur = db.cursor(buffered=True)
    try:
        cur.execute("SELECT user_id, username, password, gender FROM userdata WHERE email=%s", (email,))
        row = cur.fetchone()
        if not row:
            flash('email not found', 'registration')
            return redirect(url_for('home'))

        # unpack safely (existing users without gender will use default below)
        user_id, username, stored_hash, gender = row[0], row[1], row[2], row[3] if len(row) > 3 else 'male'
        gender = gender or 'male'

        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            session['email'] = email
            session['user_id'] = user_id
            session['username'] = username
            session['gender'] = gender
            return redirect(url_for('dashboard'))
        else:
            flash('invalid credentials', 'registration')
            return redirect(url_for('home'))
    finally:
        cur.close()
        db.close()


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'registration')
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if session.get('email') is None:
        return redirect(url_for('home'))

    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    uid = session['user_id']

    try:
        if request.method == 'POST':
            # Handle address + gender update (read-only username/email)
            address = (request.form.get('address') or '').strip()
            gender = (request.form.get('gender') or 'male').strip().lower()
            if gender not in ('male', 'female'):
                gender = 'male'  # default safety

            cur.execute(
                "UPDATE userdata SET address=%s, gender=%s WHERE user_id=%s",
                (address, gender, uid)
            )
            db.commit()
            # keep session in sync so dashboard can read it
            session['gender'] = gender
            flash('Profile updated', 'profile')

        # Fetch current profile data (including gender)
        cur.execute("""
            SELECT username, email, address, profile_pic, gender
            FROM userdata
            WHERE user_id=%s
        """, (uid,))
        user = cur.fetchone() or {}
        # default if NULL
        if not user.get('gender'):
            user['gender'] = 'male'
    finally:
        cur.close()
        db.close()

    return render_template('profile.html', user=user)

@app.route('/profile/upload', methods=['POST'])
def profile_upload():
    if session.get('email') is None:
        return redirect(url_for('home'))

    file = request.files.get('avatar')
    if not file or file.filename == '':
        flash('No file selected', 'profile')
        return redirect(url_for('profile'))
    if not allowed_image(file.filename):
        flash('Invalid image type. Allowed: png, jpg, jpeg, gif, webp', 'profile')
        return redirect(url_for('profile'))

    # Unique, safe filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    fname = f"{uuid.uuid4().hex}.{ext}"
    safe = secure_filename(fname)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], safe)

    # Prepare DB relative path we store (consistent with your code)
    rel_path = os.path.join('static', 'uploads', safe)

    db = get_db()
    cur = db.cursor(buffered=True)
    try:
        # 1) Get the current profile_pic (old) BEFORE changing it
        cur.execute("SELECT profile_pic FROM userdata WHERE user_id=%s", (session['user_id'],))
        row = cur.fetchone()
        old_rel = row[0] if row and row[0] else None

        # 2) Save new file to disk
        file.save(save_path)

        # 3) Update DB with new path
        cur.execute("UPDATE userdata SET profile_pic=%s WHERE user_id=%s", (rel_path, session['user_id']))
        db.commit()
        flash('Profile picture updated', 'profile')

        # 4) Delete old file if present and different from new
        if old_rel:
            try:
                # old_rel may be like 'static/uploads/xxx.png' or just 'uploads/xxx.png'
                # Build absolute path relative to app root
                old_abs = old_rel if os.path.isabs(old_rel) else os.path.join(app.root_path, old_rel)
                # Only delete if it's not the same as the new file (avoid accidental delete)
                new_abs = os.path.join(app.root_path, rel_path)
                if os.path.exists(old_abs) and os.path.abspath(old_abs) != os.path.abspath(new_abs):
                    os.remove(old_abs)
            except Exception as e:
                # don't break the flow if delete fails; just log
                app.logger.warning(f"Could not delete old profile pic {old_rel}: {e}")

    except Exception as e:
        db.rollback()
        flash(f'Error updating profile picture: {e}', 'profile')
    finally:
        cur.close()
        db.close()

    return redirect(url_for('profile'))

# ---------- Personal chat pages ----------
@app.route('/personal_chat_home')
def personal_chat_home():
    if session.get('email') is None:
        return redirect(url_for('home'))
    return render_template('personal_chat_home.html',user_id=session.get('user_id'),username=session.get('username'),email=session.get('email'))

@app.route('/personal_chat')
def personal_chat():
    # expects query param ?uid=<other_user_id>
    if session.get('email') is None:
        return redirect(url_for('home'))
    other_id = request.args.get('uid', type=int)
    return render_template('personal_chat.html',my_id=session.get('user_id'),other_id=other_id,username=session.get('username'))

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')
@app.route('/submit_feedback', methods=['GET','POST'])
def submit_feedback():
    if request.method == 'POST':
        db=get_db()
        feed=request.form.get('feedback')
        cursor=db.cursor(buffered=True)
        cursor.execute("select username,email from userdata where user_id=%s",(session.get('user_id'),))
        user=cursor.fetchone()
        feed=f"From: {user[0]} <{user[1]}>\n\n{feed}"
        subject="Feedback from user"
        body=f"User Feedback:\n\n{feed}"
        send_email(to="saicharanthota99@gmail.com", subject=subject, body=body)
        flash('Thank you for your feedback')
    return redirect(url_for('feedback'))
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        if not email:
            flash('Please enter your email', 'registration')
            return redirect(url_for('forgot_password'))

        db = get_db()
        cur = db.cursor(buffered=True)
        try:
            cur.execute("SELECT user_id, username FROM userdata WHERE email=%s", (email,))
            row = cur.fetchone()
            if not row:
                # Do NOT reveal that email doesn't exist (for security)
                flash('If that email exists, a reset link has been sent.', 'registration')
                return redirect(url_for('forgot_password'))

            user_id, username = row

            # Create signed token with email (and optional user_id)
            signed = generate_token({
                'email': email,
                'user_id': user_id,
                'purpose': 'password_reset'
            })

            reset_link = url_for('reset_password', token=quote_plus(signed), _external=True)

            subject = "Reset your password"
            body = (
                f"Hello {username},\n\n"
                f"We received a request to reset your password.\n\n"
                f"Click the link below to set a new password:\n{reset_link}\n\n"
                f"If you did not request this, you can ignore this email."
            )

            send_email(to=email, subject=subject, body=body)

            flash('If that email exists, a reset link has been sent.', 'registration')
            return redirect(url_for('home'))

        finally:
            cur.close()
            db.close()

    # GET
    return render_template('forgot_password.html')


# ---------- REST APIs ----------
# Search users to add to group
@app.route('/api/users/search')
def api_user_search():
    if session.get('email') is None:
        return jsonify({'error': 'login required'}), 401
    q = (request.args.get('q') or '').strip()
    me = session['user_id']
    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        cur.execute("""
            SELECT user_id, username, email
            FROM userdata
            WHERE (username LIKE %s OR email LIKE %s) AND user_id <> %s
            LIMIT 20
        """, (f'%{q}%', f'%{q}%', me))
        return {'results': cur.fetchall()}
    finally:
        cur.close()
        db.close()

# Create a group
@app.route('/api/groups', methods=['POST'])
def api_groups_create():
    if session.get('email') is None:
        return {'error': 'login required'}, 401

    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    members = data.get('members') or []

    if not name or not members:
        return {'error': 'group name and members required'}, 400

    me = session['user_id']
    db = get_db()
    cur = db.cursor(buffered=True)
    try:

        # 🔥 Check if group name already exists (global unique)
        cur.execute("SELECT 1 FROM chat_group WHERE name=%s LIMIT 1", (name,))
        if cur.fetchone():
            return {'error': 'group name already exists'}, 409

        # create group
        cur.execute("INSERT INTO chat_group (name, created_by) VALUES (%s, %s)", (name, me))
        gid = cur.lastrowid

        # include creator as member too
        uni = set(members + [me])
        for uid in uni:
            cur.execute("INSERT IGNORE INTO group_member (group_id, user_id) VALUES (%s, %s)", (gid, uid))

        db.commit()
        return {'ok': True, 'group_id': gid}

    except Exception as e:
        db.rollback()
        return {'error': str(e)}, 500

    finally:
        cur.close()
        db.close()



# List MY groups with unread count, last activity, and member emails
@app.route('/api/groups', methods=['GET'])
def api_groups_list():
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    me = session['user_id']
    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        # groups I belong to
        cur.execute("""
            SELECT g.id, g.name, g.created_by,
                   COALESCE((SELECT MAX(created_at) FROM message WHERE group_id=g.id), g.created_at) AS last_activity
            FROM chat_group g
            JOIN group_member gm ON gm.group_id=g.id AND gm.user_id=%s
            ORDER BY last_activity DESC
        """, (me,))
        groups = cur.fetchall()

        # unread and member emails per group
        for g in groups:
            gid = g['id']
            # unread
            cur2 = db.cursor()
            cur2.execute("""
                SELECT COUNT(*)
                FROM message m
                JOIN message_read mr ON mr.message_id = m.id AND mr.user_id = %s
                WHERE m.group_id = %s AND mr.read_at IS NULL
            """, (me, gid))
            g['unread'] = cur2.fetchone()[0]
            cur2.close()

            # member emails (including creator)
            cur3 = db.cursor()
            cur3.execute("""
                SELECT u.email
                FROM group_member gm
                JOIN userdata u ON u.user_id = gm.user_id
                WHERE gm.group_id = %s
            """, (gid,))
            emails = [r[0] for r in cur3.fetchall()]
            cur3.close()
            g['member_emails'] = emails

            # coerce datetime to string for JSON safety
            if isinstance(g.get('last_activity'), datetime):
                g['last_activity'] = g['last_activity'].isoformat(sep=' ', timespec='seconds')

        return {'groups': groups}
    finally:
        cur.close()
        db.close()

# Get one group with last messages and members
@app.route('/api/groups/<int:group_id>', methods=['GET'])
def api_group_detail(group_id):
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    me = session['user_id']
    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        # membership check
        cur.execute("SELECT 1 FROM group_member WHERE group_id=%s AND user_id=%s", (group_id, me))
        if not cur.fetchone():
            return {'error': 'not a member'}, 403

        cur.execute("SELECT id, name, created_by, created_at FROM chat_group WHERE id=%s", (group_id,))
        g = cur.fetchone()

        cur.execute("""
            SELECT u.user_id, u.username, u.email
            FROM group_member gm
            JOIN userdata u ON u.user_id = gm.user_id
            WHERE gm.group_id=%s
        """, (group_id,))
        members = cur.fetchall()

        cur.execute("""
            SELECT m.id, m.sender_id, u.username AS sender_name, m.content, m.file_path, m.created_at
            FROM message m
            JOIN userdata u ON u.user_id = m.sender_id
            WHERE m.group_id=%s
            ORDER BY m.created_at DESC
            LIMIT 100
        """, (group_id,))
        msgs = list(reversed(cur.fetchall()))

        # convert timestamps to strings
        for m in msgs:
            if isinstance(m.get('created_at'), datetime):
                m['created_at'] = m['created_at'].isoformat(sep=' ', timespec='seconds')

        return {'group': g, 'members': members, 'messages': msgs}
    finally:
        cur.close()
        db.close()

# Delete a group (only creator can delete)
@app.route('/api/groups/<int:group_id>', methods=['DELETE'])
def api_group_delete(group_id):
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    me = session['user_id']
    db = get_db()
    cur = db.cursor(buffered=True)
    try:
        cur.execute("SELECT created_by FROM chat_group WHERE id=%s", (group_id,))
        row = cur.fetchone()
        if not row:
            return {'error': 'group not found'}, 404
        creator = row[0]
        if creator != me:
            return {'error': 'only creator can delete this group'}, 403
        cur.execute("DELETE FROM chat_group WHERE id=%s", (group_id,))
        db.commit()
        return {'ok': True}
    except Exception as e:
        db.rollback()
        return {'error': str(e)}, 500
    finally:
        cur.close()
        db.close()

# Search users for personal chat (reuse pattern you used)
@app.route('/api/personal/search')
def api_personal_search():
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    q = (request.args.get('q') or '').strip()
    me = session['user_id']
    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        cur.execute("""
            SELECT DISTINCT user_id, username, email, profile_pic
            FROM userdata
            WHERE (username LIKE %s OR email LIKE %s) AND user_id <> %s
            LIMIT 20
        """, (f'%{q}%', f'%{q}%', me))
        return {'results': cur.fetchall()}
    finally:
        cur.close()
        db.close()

# Get or create private chat and return messages
@app.route('/api/personal/get_chat/<int:uid>')
def api_personal_get_chat(uid):
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    me = session['user_id']
    if me == uid:
        return {'error': 'cannot chat with yourself'}, 400

    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        # find existing chat (unordered pair)
        cur.execute("""
            SELECT chat_id FROM private_chat
            WHERE (user1=%s AND user2=%s) OR (user1=%s AND user2=%s)
            LIMIT 1
        """, (me, uid, uid, me))
        row = cur.fetchone()
        if row:
            chat_id = row['chat_id']
        else:
            # create new chat with smaller id first to keep uniqueness (optional)
            cur.execute("INSERT INTO private_chat (user1, user2) VALUES (%s, %s)", (me, uid))
            chat_id = cur.lastrowid
            db.commit()

        # fetch messages
        cur.execute("""
            SELECT pm.id, pm.chat_id, pm.sender_id, u.username as sender_name, u.profile_pic,
                   pm.content, pm.file_path, pm.created_at
            FROM private_message pm
            JOIN userdata u ON pm.sender_id = u.user_id
            WHERE pm.chat_id = %s
            ORDER BY pm.created_at ASC
        """, (chat_id,))
        msgs = cur.fetchall()

        # serialise timestamps to string
        for m in msgs:
            if isinstance(m.get('created_at'), datetime):
                m['created_at'] = m['created_at'].isoformat(sep=' ', timespec='seconds')

        # also return the other user's basic info
        cur.execute("SELECT user_id, username, email, profile_pic FROM userdata WHERE user_id=%s", (uid,))
        other = cur.fetchone()

        return {'chat_id': chat_id, 'messages': msgs, 'other': other}
    finally:
        cur.close()
        db.close()

@app.route('/api/personal/recent')
def api_personal_recent():
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    me = session['user_id']
    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        # Join private_chat with last message per chat, and give the other participant info.
        cur.execute("""
            SELECT pc.chat_id,
                   CASE WHEN pc.user1=%s THEN pc.user2 ELSE pc.user1 END AS user_id,
                   u.username, u.profile_pic,
                   (SELECT pm.content FROM private_message pm WHERE pm.chat_id=pc.chat_id ORDER BY pm.created_at DESC LIMIT 1) AS last_message_preview,
                   (SELECT pm.created_at FROM private_message pm WHERE pm.chat_id=pc.chat_id ORDER BY pm.created_at DESC LIMIT 1) AS last_at
            FROM private_chat pc
            JOIN userdata u ON u.user_id = (CASE WHEN pc.user1=%s THEN pc.user2 ELSE pc.user1 END)
            WHERE pc.user1=%s OR pc.user2=%s
            ORDER BY last_at DESC
            LIMIT 50
        """, (me, me, me, me))
        rows = cur.fetchall()
        for r in rows:
            if isinstance(r.get('last_at'), datetime):
                r['last_at'] = r['last_at'].isoformat(sep=' ', timespec='seconds')
        return {'results': rows}
    finally:
        cur.close()
        db.close()

@app.route('/api/personal/upload', methods=['POST'])
def api_personal_upload():
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    
    file = request.files.get('file')
    chat_id = request.form.get('chat_id', type=int)
    
    if not file or file.filename == '':
        return {'error': 'No file selected'}, 400
    if not chat_id:
        return {'error': 'No chat_id'}, 400
    
    # Allow common file types (images + documents)
    allowed_exts = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg', 'gif', 'zip'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if ext not in allowed_exts:
        return {'error': f'File type not allowed. Allowed: {", ".join(allowed_exts)}'}, 400
    
    # Generate safe filename
    fname = f"{uuid.uuid4().hex}.{ext}"
    safe = secure_filename(fname)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], safe)
    rel_path = f'/{os.path.join("static", "uploads", safe)}'
    
    try:
        file.save(save_path)
        # Optionally store file record in DB (depends on your schema)
        return {'ok': True, 'file_path': rel_path}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/group/upload', methods=['POST'])
def api_group_upload():
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    
    file = request.files.get('file')
    group_id = request.form.get('group_id', type=int)
    
    if not file or file.filename == '':
        return {'error': 'No file selected'}, 400
    if not group_id:
        return {'error': 'No group_id'}, 400
    
    # Verify user is member of group
    db = get_db()
    cur = db.cursor(buffered=True)
    try:
        cur.execute("SELECT 1 FROM group_member WHERE group_id=%s AND user_id=%s", (group_id, session['user_id']))
        if not cur.fetchone():
            return {'error': 'Not a group member'}, 403
    finally:
        cur.close()
        db.close()
    
    # Allow common file types
    allowed_exts = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg', 'gif', 'zip'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if ext not in allowed_exts:
        return {'error': f'File type not allowed. Allowed: {", ".join(allowed_exts)}'}, 400
    
    # Generate safe filename
    fname = f"{uuid.uuid4().hex}.{ext}"
    safe = secure_filename(fname)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], safe)
    rel_path = f'/{os.path.join("static", "uploads", safe)}'
    
    try:
        file.save(save_path)
        return {'ok': True, 'file_path': rel_path}
    except Exception as e:
        return {'error': str(e)}, 500
    
@app.route('/api/personal/status/<int:uid>')
def api_personal_status(uid):
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    return {'user_id': uid, 'online': uid in online_users}

@app.route('/api/personal/clear_chat/<int:chat_id>', methods=['DELETE'])
def api_personal_clear_chat(chat_id):
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    me = session['user_id']

    db = get_db()
    cur = db.cursor(buffered=True)
    try:
        # ensure user is part of this chat
        cur.execute("SELECT user1, user2 FROM private_chat WHERE chat_id=%s", (chat_id,))
        row = cur.fetchone()
        if not row:
            return {'error': 'chat not found'}, 404

        if me not in row:
            return {'error': 'not a participant of this chat'}, 403

        cur.execute("DELETE FROM private_message WHERE chat_id=%s", (chat_id,))
        db.commit()
        return {'ok': True}
    except Exception as e:
        db.rollback()
        return {'error': str(e)}, 500
    finally:
        cur.close()
        db.close()

@app.route('/api/groups/<int:group_id>/online')
def api_group_online(group_id):
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    me = session['user_id']

    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        # ensure user is in this group
        cur.execute("""
            SELECT 1 FROM group_member
            WHERE group_id=%s AND user_id=%s
            LIMIT 1
        """, (group_id, me))
        if not cur.fetchone():
            return {'error': 'not a member'}, 403

        # get all members
        cur.execute("""
            SELECT u.user_id, u.username, u.email
            FROM group_member gm
            JOIN userdata u ON u.user_id = gm.user_id
            WHERE gm.group_id=%s
        """, (group_id,))
        members = cur.fetchall()

        # mark which are online (using online_users set)
        online = [m for m in members if m['user_id'] in online_users]
        return {'online': online}
    finally:
        cur.close()
        db.close()

@app.route('/api/groups/<int:group_id>/leave', methods=['POST'])
def api_group_leave(group_id):
    if session.get('email') is None:
        return {'error': 'login required'}, 401
    me = session['user_id']

    db = get_db()
    cur = db.cursor(buffered=True)
    try:
        # ensure group exists
        cur.execute("SELECT created_by FROM chat_group WHERE id=%s", (group_id,))
        row = cur.fetchone()
        if not row:
            return {'error': 'group not found'}, 404
        creator = row[0]

        # ensure user is member
        cur.execute("SELECT 1 FROM group_member WHERE group_id=%s AND user_id=%s", (group_id, me))
        if not cur.fetchone():
            return {'error': 'not a member'}, 403

        # remove from group_member
        cur.execute("DELETE FROM group_member WHERE group_id=%s AND user_id=%s", (group_id, me))

        # if no members left, delete the group entirely (optional)
        cur.execute("SELECT COUNT(*) FROM group_member WHERE group_id=%s", (group_id,))
        remaining = cur.fetchone()[0]
        if remaining == 0:
            cur.execute("DELETE FROM chat_group WHERE id=%s", (group_id,))

        db.commit()
        return {'ok': True}
    except Exception as e:
        db.rollback()
        return {'error': str(e)}, 500
    finally:
        cur.close()
        db.close()
        
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        data = verify_token(data=token)
    except Exception:
        flash('Invalid or expired reset link', 'registration')
        return redirect(url_for('home'))

    # Optional: ensure correct purpose
    if data.get('purpose') != 'password_reset':
        flash('Invalid reset token', 'registration')
        return redirect(url_for('home'))

    email = data.get('email')

    if request.method == 'POST':
        new_password = (request.form.get('password') or '').strip()
        confirm = (request.form.get('confirm') or '').strip()

        if not new_password or not confirm:
            flash('Please fill both password fields', 'registration')
            return redirect(url_for('reset_password', token=token))

        if new_password != confirm:
            flash('Passwords do not match', 'registration')
            return redirect(url_for('reset_password', token=token))

        # Update password in DB
        db = get_db()
        cur = db.cursor(buffered=True)
        try:
            hash_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute("UPDATE userdata SET password=%s WHERE email=%s", (hash_password, email))
            db.commit()
            flash('Password reset successfully. Please login.', 'registration')
            return redirect(url_for('home'))
        except Exception:
            db.rollback()
            flash('Could not reset password, try again.', 'registration')
            return redirect(url_for('reset_password', token=token))
        finally:
            cur.close()
            db.close()

    # GET
    return render_template('reset_password.html', email=email)


# ---------- Socket.IO ----------
@socketio.on('connect')
def sio_connect():
    uid = session.get('user_id')
    if uid is None:
        return False  # reject not-logged-in connections

    # mark user online
    online_users.add(uid)
    join_room(f"user:{uid}")
    # notify watchers of this user
    emit('presence', {'user_id': uid, 'status': 'online'}, room=f"user:{uid}", include_self=False)


@socketio.on('join_group')
def sio_join_group(data):
    gid = int(data.get('group_id'))
    uid = session.get('user_id')
    if not uid:
        emit('error', {'message': 'not logged in'})
        return
        

    db = get_db()
    cur = db.cursor(buffered=True)
    try:
        cur.execute("SELECT 1 FROM group_member WHERE group_id=%s AND user_id=%s", (gid, uid))
        if not cur.fetchone():
            emit('error', {'message': 'Not a member'})
            return
        join_room(f"group:{gid}")
        emit('system', {'message': f"{session.get('username','Someone')} joined"}, room=f"group:{gid}", include_self=False)
    finally:
        cur.close()
        db.close()

@socketio.on('private_typing')
def sio_private_typing(data):
    chat_id = data.get('chat_id')
    uid = session.get('user_id')
    if not uid or not chat_id:
        return
    try:
        chat_id = int(chat_id)
    except ValueError:
        return

    emit(
        'private_typing',
        {
            'chat_id': chat_id,
            'user_id': uid,
            'username': session.get('username', 'Someone')
        },
        room=f"private:{chat_id}",
        include_self=False
    )


@socketio.on('private_stop_typing')
def sio_private_stop_typing(data):
    chat_id = data.get('chat_id')
    uid = session.get('user_id')
    if not uid or not chat_id:
        return
    try:
        chat_id = int(chat_id)
    except ValueError:
        return

    emit(
        'private_stop_typing',
        {
            'chat_id': chat_id,
            'user_id': uid
        },
        room=f"private:{chat_id}",
        include_self=False
    )

@socketio.on('edit_private_message')
def sio_edit_private_message(data):
    uid = session.get('user_id')
    if not uid:
        return

    chat_id = data.get('chat_id')
    msg_id = data.get('message_id')
    new_content = (data.get('content') or '').strip()

    if not chat_id or not msg_id or not new_content:
        return

    try:
        chat_id = int(chat_id)
        msg_id = int(msg_id)
    except ValueError:
        return

    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        # ensure message belongs to this chat and this user is the sender
        cur.execute("SELECT chat_id, sender_id FROM private_message WHERE id=%s", (msg_id,))
        row = cur.fetchone()
        if not row or row['chat_id'] != chat_id or row['sender_id'] != uid:
            emit('error', {'message': 'cannot edit this message'})
            return

        cur.execute("UPDATE private_message SET content=%s WHERE id=%s", (new_content, msg_id))
        db.commit()

        # fetch updated message
        cur.execute("""
            SELECT pm.id, pm.chat_id, pm.sender_id, u.username AS sender_name, u.profile_pic,
                   pm.content, pm.file_path, pm.created_at
            FROM private_message pm
            JOIN userdata u ON u.user_id = pm.sender_id
            WHERE pm.id=%s
        """, (msg_id,))
        msg = cur.fetchone()
        if isinstance(msg.get('created_at'), datetime):
            msg['created_at'] = msg['created_at'].isoformat(sep=' ', timespec='seconds')

        emit('private_message_edited', msg, room=f"private:{chat_id}")
    finally:
        cur.close()
        db.close()

@socketio.on('leave_group')
def sio_leave_group(data):
    gid = int(data.get('group_id'))
    leave_room(f"group:{gid}")
    emit('system', {'message': f"{session.get('username','Someone')} left the group"}, room=f"group:{gid}", include_self=False)

@socketio.on('disconnect')
def sio_disconnect():
    uid = session.get('user_id')
    if not uid:
        return
    online_users.discard(uid)
    # notify anyone watching this user
    emit('presence', {'user_id': uid, 'status': 'offline'}, room=f"user:{uid}", include_self=False)

@socketio.on('edit_group_message')
def sio_edit_group_message(data):
    uid = session.get('user_id')
    if not uid:
        return

    group_id = data.get('group_id')
    msg_id = data.get('message_id')
    new_content = (data.get('content') or '').strip()

    if not group_id or not msg_id or not new_content:
        return

    try:
        group_id = int(group_id)
        msg_id = int(msg_id)
    except ValueError:
        return

    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        # ensure message exists and belongs to this group and this user is sender
        cur.execute("SELECT group_id, sender_id FROM message WHERE id=%s", (msg_id,))
        row = cur.fetchone()
        if not row or row['group_id'] != group_id or row['sender_id'] != uid:
            emit('error', {'message': 'cannot edit this message'})
            return

        cur.execute("UPDATE message SET content=%s WHERE id=%s", (new_content, msg_id))
        db.commit()

        # fetch updated message with sender info
        cur.execute("""
            SELECT m.id, m.sender_id, u.username AS sender_name, m.content, m.file_path, m.created_at
            FROM message m
            JOIN userdata u ON u.user_id = m.sender_id
            WHERE m.id=%s
        """, (msg_id,))
        msg = cur.fetchone()
        if isinstance(msg.get('created_at'), datetime):
            msg['created_at'] = msg['created_at'].isoformat(sep=' ', timespec='seconds')

        emit('group_message_edited', msg, room=f"group:{group_id}")
    finally:
        cur.close()
        db.close()

@socketio.on('watch_user')
def sio_watch_user(data):
    uid = session.get('user_id')
    if not uid:
        return
    other_id = data.get('user_id')
    if not other_id:
        return
    try:
        other_id = int(other_id)
    except ValueError:
        return

    # join a room that receives presence updates about "other_id"
    join_room(f"user:{other_id}")

    # send immediate presence status to this socket
    status = 'online' if other_id in online_users else 'offline'
    emit('presence', {'user_id': other_id, 'status': status})

@socketio.on('send_message')
def sio_send_message(data):
    gid = int(data.get('group_id'))
    content = (data.get('content') or '').strip()
    file_path = data.get('file_path', '')  # Optional file attachment
    uid = session.get('user_id')
    if not uid or not content:
        return

    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        # member check
        cur.execute("SELECT 1 FROM group_member WHERE group_id=%s AND user_id=%s", (gid, uid))
        if not cur.fetchone():
            emit('error', {'message': 'Not a member'})
            return

        # insert message (with file_path if table supports it, otherwise just content)
        try:
            cur.execute("INSERT INTO message (group_id, sender_id, content, file_path) VALUES (%s, %s, %s, %s)", (gid, uid, content, file_path if file_path else None))
        except:
            # Fallback if file_path column doesn't exist
            cur.execute("INSERT INTO message (group_id, sender_id, content) VALUES (%s, %s, %s)", (gid, uid, content))
        msg_id = cur.lastrowid

        # unread rows
        cur2 = db.cursor(buffered=True)
        cur2.execute("SELECT user_id FROM group_member WHERE group_id=%s", (gid,))
        member_ids = [r[0] for r in cur2.fetchall()]
        cur2.close()
        for mid in member_ids:
            cur3 = db.cursor(buffered=True)
            cur3.execute(
                "INSERT IGNORE INTO message_read (message_id, user_id, read_at) VALUES (%s, %s, NULL)",
                (msg_id, mid)
            )
            cur3.close()
        db.commit()

        # fetch enriched msg
        try:
            cur.execute("""
                SELECT m.id, m.sender_id, u.username AS sender_name, m.content, m.file_path, m.created_at
                FROM message m JOIN userdata u ON u.user_id=m.sender_id
                WHERE m.id=%s
            """, (msg_id,))
        except:
            # Fallback if file_path doesn't exist - still try to get it, default to NULL
            cur.execute("""
                SELECT m.id, m.sender_id, u.username AS sender_name, m.content, NULL AS file_path, m.created_at
                FROM message m JOIN userdata u ON u.user_id=m.sender_id
                WHERE m.id=%s
            """, (msg_id,))
        msg = cur.fetchone()

        # make created_at serializable
        if isinstance(msg.get('created_at'), datetime):
            msg['created_at'] = msg['created_at'].isoformat(sep=' ', timespec='seconds')

        emit("new_message", msg, room=f"group:{gid}")

        # mark sender read for his own message
        cur4 = db.cursor(buffered=True)
        cur4.execute("""
            UPDATE message_read SET read_at=CURRENT_TIMESTAMP
            WHERE message_id=%s AND user_id=%s AND read_at IS NULL
        """, (msg_id, uid))
        db.commit()
        cur4.close()

    finally:
        cur.close()
        db.close()

@socketio.on('mark_read')
def sio_mark_read(data):
    gid = int(data.get('group_id'))
    uid = session.get('user_id')
    if not uid:
        return
    db = get_db()
    cur = db.cursor(buffered=True)
    try:
        cur.execute("""
          UPDATE message_read mr
          JOIN message m ON m.id = mr.message_id
          SET mr.read_at = CURRENT_TIMESTAMP
          WHERE mr.user_id=%s AND m.group_id=%s AND mr.read_at IS NULL
        """, (uid, gid))
        db.commit()
    finally:
        cur.close()
        db.close()

@socketio.on('typing')
def sio_typing(data):
    gid = int(data.get('group_id'))
    uid = session.get('user_id')
    username = session.get('username', 'Someone')
    if not uid:
        return
    # Broadcast typing indicator to other users in group
    emit('user_typing', {'username': username, 'user_id': uid}, room=f"group:{gid}", include_self=False)

@socketio.on('stop_typing')
def sio_stop_typing(data):
    gid = int(data.get('group_id'))
    uid = session.get('user_id')
    if not uid:
        return
    # Broadcast stop typing to other users in group
    emit('user_stop_typing', {'user_id': uid}, room=f"group:{gid}", include_self=False)

@socketio.on('join_private')
def sio_join_private(data):
    chat_id = int(data.get('chat_id'))
    uid = session.get('user_id')
    if not uid:
        emit('error', {'message': 'not logged in'})
        return
    # optional membership check: ensure chat exists and user belongs to it
    db = get_db()
    cur = db.cursor(buffered=True)
    try:
        cur.execute("SELECT 1 FROM private_chat WHERE chat_id=%s AND (user1=%s OR user2=%s)", (chat_id, uid, uid))
        if not cur.fetchone():
            emit('error', {'message': 'Not part of this chat'})
            return
        join_room(f"private:{chat_id}")
        emit('system', {'message': f"{session.get('username','Someone')} joined"}, room=f"private:{chat_id}", include_self=False)
    finally:
        cur.close()
        db.close()

@socketio.on('private_message')
def sio_private_message(data):
    chat_id = int(data.get('chat_id'))
    content = (data.get('content') or '').strip()
    file_path = data.get('file_path')
    sender = session.get('user_id')
    if not sender or not content:
        return

    db = get_db()
    cur = db.cursor(dictionary=True, buffered=True)
    try:
        # ensure sender is part of chat
        cur.execute("SELECT 1 FROM private_chat WHERE chat_id=%s AND (user1=%s OR user2=%s)", (chat_id, sender, sender))
        if not cur.fetchone():
            emit('error', {'message': 'Not a member of chat'})
            return

        if file_path:
            cur.execute("INSERT INTO private_message (chat_id, sender_id, content, file_path) VALUES (%s, %s, %s, %s)", (chat_id, sender, content, file_path))
        else:
            cur.execute("INSERT INTO private_message (chat_id, sender_id, content) VALUES (%s, %s, %s)", (chat_id, sender, content))
        msg_id = cur.lastrowid
        db.commit()

        # fetch enriched message
        cur.execute("""
            SELECT pm.id, pm.chat_id, pm.sender_id, u.username AS sender_name, u.profile_pic,
                   pm.content, pm.file_path, pm.created_at
            FROM private_message pm JOIN userdata u ON u.user_id = pm.sender_id
            WHERE pm.id=%s
        """, (msg_id,))
        msg = cur.fetchone()
        if isinstance(msg.get('created_at'), datetime):
            msg['created_at'] = msg['created_at'].isoformat(sep=' ', timespec='seconds')

        emit('private_new_message', msg, room=f"private:{chat_id}")

    finally:
        cur.close()
        db.close()


if __name__ == '__main__':
    # Render (or any cloud host) will set the PORT env variable
    port = int(os.environ.get("PORT"))
    socketio.run(
        app,
        host="0.0.0.0",  # listen on all interfaces
        port=port,
        debug=False,     # turn off debug in production
        use_reloader=False
    )

