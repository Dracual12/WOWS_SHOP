from functools import wraps
from flask import session, redirect, url_for, current_app
from ..config import Config

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            current_app.logger.warning('Попытка доступа к админ-панели без авторизации')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def login_admin():
    session['admin_logged_in'] = True
    current_app.logger.info('Администратор успешно авторизован')

def logout_admin():
    session.pop('admin_logged_in', None)
    current_app.logger.info('Администратор вышел из системы')

def is_admin_logged_in():
    return session.get('admin_logged_in', False) 