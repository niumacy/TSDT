from fabric.contrib.files import append, contains, sed, exists
from fabric.api import env, local, run, cd
import random
import shlex  # 新增导入
from fabric.api import hide

REPO_URL = 'https://github.com/niumacy/TSDT.git/'

def deploy():
    env.user = 'cy'  # 明确设置用户名
    env.host = '121.40.213.11'  # 可改为通过参数传递，如 fab deploy:host=xxx
    site_folder = f'/home/{env.user}/sites/{env.host}'
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)

def _create_directory_structure_if_necessary(site_folder):
    escaped_site = shlex.quote(site_folder)
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        run(f'mkdir -p {escaped_site}/{subfolder}')

def _get_latest_source(source_folder):
    escaped_source = shlex.quote(source_folder)
    if exists(f'{escaped_source}/.git'):
        with cd(escaped_source):
            run('git fetch origin main')
    else:
        run(f'git clone {REPO_URL} {escaped_source}')
    with cd(escaped_source):
        # 修改这一行，使用hide上下文管理器捕获输出
        with hide('running', 'stdout'):
            current_commit = run('git rev-parse origin/main')
        run(f'git reset --hard {current_commit}')

def _update_settings(source_folder, site_name):
    settings_path = f"{source_folder}/notes/settings.py"
    secret_key_file = f"{source_folder}/notes/secret_key.py"

    # ------------------------
    # 1. 修改 DEBUG 模式
    # ------------------------
    if contains(settings_path, "DEBUG = True"):
        # 使用双引号包裹，避免单引号与转义冲突
        sed(settings_path, 'DEBUG = True', 'DEBUG = False', use_sudo=False)

    # ------------------------
    # 2. 安全设置 ALLOWED_HOSTS
    # ------------------------
    # 先移除旧的 ALLOWED_HOSTS 配置（如果存在）
    if contains(settings_path, 'ALLOWED_HOSTS ='):
        sed(settings_path, '^ALLOWED_HOSTS = .*', '', use_sudo=False)
    
    # 添加新的 ALLOWED_HOSTS（使用单引号包裹列表，避免双引号转义问题）
    append(
        settings_path,
        f'ALLOWED_HOSTS = ["{site_name}", "localhost", "127.0.0.1"]',
        escape=False,
        use_sudo=False
    )

    # ------------------------
    # 3. 管理 SECRET_KEY
    # ------------------------
    if not exists(secret_key_file):
        # 生成安全密钥
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, f'SECRET_KEY = "{key}"', use_sudo=False)
    
    # 确保导入 SECRET_KEY（避免重复添加）
    if not contains(settings_path, 'from .secret_key import SECRET_KEY'):
        append(settings_path, '\nfrom .secret_key import SECRET_KEY', use_sudo=False)

def _update_virtualenv(source_folder):
    virtualenv_folder = f'{source_folder}/../virtualenv'
    escaped_virtualenv = shlex.quote(virtualenv_folder)
    if not exists(f'{escaped_virtualenv}/bin/pip'):
        run(f'python3 -m venv {escaped_virtualenv}')  # 使用 python3 通用路径
    run(
        f'{escaped_virtualenv}/bin/pip install -r '
        f'{shlex.quote(source_folder)}/requirements.txt'
    )

def _update_static_files(source_folder):
    with cd(source_folder):
        run('../virtualenv/bin/python manage.py collectstatic --noinput')

def _update_database(source_folder):
    with cd(source_folder):
        run('../virtualenv/bin/python manage.py migrate --noinput')