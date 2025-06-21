import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, abort
from flask_socketio import emit, join_room
from werkzeug.utils import secure_filename
from extensions import db, socketio
from models import Post, Comment, UserLike, Group, GroupMessage, GroupMessageLike

# Configurations & Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///desabafos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize extensions
db.init_app(app)
socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')

import uuid

# In-memory storage for connected users and their IDs
active_users = {}  # {sid: {'username': username, 'user_id': user_id}}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/groups')
def groups():
    try:
        groups = Group.query.order_by(Group.created_at.desc()).all()
        return render_template('groups.html', groups=groups)
    except Exception as e:
        app.logger.error(f"Error fetching groups: {e}")
        abort(500)

@app.route('/group/<int:group_id>')
def group_chat(group_id):
    try:
        group = Group.query.get_or_404(group_id)
        messages = GroupMessage.query.filter_by(group_id=group_id).order_by(GroupMessage.created_at).all()
        return render_template('group_chat.html', group=group, messages=messages)
    except Exception as e:
        app.logger.error(f"Error fetching group chat: {e}")
        abort(500)

@app.route('/create_group', methods=['POST'])
def create_group():
    try:
        name = request.form.get('name')
        if not name:
            return jsonify({'error': 'Nome do grupo é obrigatório'}), 400

        file = request.files.get('image')
        image_path = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = os.path.join('uploads', filename)

        group = Group(name=name, image_path=image_path)
        db.session.add(group)
        db.session.commit()

        return redirect(url_for('groups'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating group: {e}")
        return jsonify({'error': 'Erro ao criar grupo'}), 500

@app.route('/like_message/<int:message_id>', methods=['POST'])
def like_message(message_id):
    try:
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # Check if user already liked this message
        existing_like = GroupMessageLike.query.filter_by(message_id=message_id, user_id=user_id).first()
        if existing_like:
            return jsonify({'error': 'Você já curtiu esta mensagem'}), 400

        message = GroupMessage.query.get_or_404(message_id)
        message.likes += 1
        message_like = GroupMessageLike(message_id=message_id, user_id=user_id)
        db.session.add(message_like)
        db.session.commit()

        # Emit updated like count to all clients in the group
        socketio.emit('update_likes', {
            'message_id': message_id,
            'likes': message.likes
        }, room=f'group_{message.group_id}')
        
        return jsonify({'likes': message.likes})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error liking message: {e}")
        return jsonify({'error': 'Erro ao processar o like'}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        group_id = request.form.get('group_id')
        username = request.form.get('username')
        content = request.form.get('content')
        
        if not all([group_id, username]):
            return jsonify({'error': 'Dados incompletos'}), 400

        file = request.files.get('image')
        image_path = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = os.path.join('uploads', filename)

        message = GroupMessage(
            group_id=group_id,
            username=username,
            content=content,
            image_path=image_path
        )
        db.session.add(message)
        db.session.commit()

        # Emit new message to all clients in the group
        socketio.emit('new_message', {
            'id': message.id,
            'username': message.username,
            'content': message.content,
            'image_path': url_for('static', filename=message.image_path) if message.image_path else None,
            'created_at': message.created_at.strftime("%H:%M"),
            'likes': message.likes
        }, room=f'group_{group_id}')

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error sending message: {e}")
        return jsonify({'error': 'Erro ao enviar mensagem'}), 500

@socketio.on('join_group')
def handle_join_group(data):
    group_id = data.get('group_id')
    if group_id:
        join_room(f'group_{group_id}')

@app.route('/')
def index():
    try:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        posts_with_comments = []
        for post in posts:
            comment_count = Comment.query.filter_by(post_id=post.id).count()
            posts_with_comments.append({
                'post': post,
                'comment_count': comment_count
            })
        vent_count = Post.query.count()
        return render_template('index.html', posts=posts_with_comments, vent_count=vent_count)
    except Exception as e:
        app.logger.error(f"Error fetching posts: {e}")
        abort(500)

@app.route('/post', methods=['POST'])
def create_post():
    try:
        username = request.form.get('username')
        if not username:
            return jsonify({'error': 'Username is required'}), 400
            
        content = request.form.get('content')
        file = request.files.get('image')
        image_path = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = os.path.join('uploads', filename)

        post = Post(username=username, content=content, image_path=image_path)
        db.session.add(post)
        db.session.commit()
        
        # Emit new post to all clients
        socketio.emit('new_post', {
            'id': post.id,
            'username': post.username,
            'content': post.content,
            'image_path': url_for('static', filename=post.image_path) if post.image_path else None,
            'likes': 0,
            'created_at': post.created_at.strftime("%d/%m/%Y %H:%M")
        })
        
        # Emit updated vent count
        new_vent_count = Post.query.count()
        socketio.emit('update_vent_count', {'vent_count': new_vent_count})
        
        flash("Seu desabafo foi publicado!", "success")
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating post: {e}")
        flash("Houve um erro ao publicar seu desabafo.", "danger")
        return redirect(url_for('index'))

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    try:
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # Check if user already liked this post
        existing_like = UserLike.query.filter_by(post_id=post_id, user_id=user_id).first()
        if existing_like:
            return jsonify({'error': 'Você já curtiu este post'}), 400

        post = Post.query.get_or_404(post_id)
        post.likes += 1
        user_like = UserLike(post_id=post_id, user_id=user_id)
        db.session.add(user_like)
        db.session.commit()
        
        return jsonify({'likes': post.likes})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error liking post: {e}")
        return jsonify({'error': 'Erro ao processar o like.'}), 500

@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        username = request.form.get('username', '').strip()
        comment_text = request.form.get('comment')
        parent_id = request.form.get('parent_id')
        
        if not comment_text:
            return jsonify({'error': 'Comentário vazio'}), 400
        
        if not username:
            return jsonify({'error': 'Nome de usuário é obrigatório'}), 400

        comment = Comment(
            post_id=post.id,
            username=username,
            content=comment_text,
            parent_id=parent_id if parent_id else None
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'id': comment.id,
            'username': comment.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime("%d/%m/%Y %H:%M"),
            'parent_id': comment.parent_id
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding comment: {e}")
        return jsonify({'error': 'Erro ao adicionar comentário.'}), 500

@app.route('/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        comments = [{
            'id': c.id,
            'username': c.username,
            'content': c.content,
            'created_at': c.created_at.strftime("%d/%m/%Y %H:%M"),
            'parent_id': c.parent_id
        } for c in post.comments]
        return jsonify(comments)
    except Exception as e:
        app.logger.error(f"Error getting comments: {e}")
        return jsonify({'error': 'Erro ao obter comentários.'}), 500

@socketio.on('register_user')
def handle_register(data):
    user_id = str(uuid.uuid4())[:8]  # Using first 8 characters of UUID
    formatted_username = f"#anon_{user_id}"
    active_users[request.sid] = {
        'username': formatted_username,
        'user_id': user_id
    }
    emit('user_registered', {
        'username': formatted_username,
        'user_id': user_id
    })
    emit('update_users', {'active_users': len(active_users)}, broadcast=True)

@socketio.on('connect')
def handle_connect():
    emit('update_users', {'active_users': len(active_users)}, broadcast=True)
    
@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_users:
        del active_users[request.sid]
    emit('update_users', {'active_users': len(active_users)}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, port=8000)
