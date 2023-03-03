from flask import Flask, render_template, request, url_for, flash, redirect, send_file
import json, os, base64, time
from threading import Thread

app = Flask(__name__)


@app.route('/')
def entry():
    vars = []
    descriptions = []
    placeholders = []
    with open('app.json', 'r') as f:
        file = json.load(f)
    for var in file['env']:
        vars.append(var)
        description = file['env'][var]['description']
        descriptions.append(description)
        placeholder = file['env'][var]['value']
        placeholders.append(placeholder)
    random_string = str(os.urandom(4).hex())
    folder = os.urandom(16).hex()
    return render_template('fly.toml-generator.html', len=len(vars), vars=vars, descriptions=descriptions, placeholders=placeholders, rand=random_string, folder=folder)

@app.route('/submit', methods=['POST'])
def submit():
    
    def cleanup():
        time.sleep(15)
        os.system('rm -rf static/*')

    FOLDER = request.form.get('FOLDER')
    os.mkdir('static')
    os.mkdir('static/' + FOLDER)
    cert_file = request.files.get('APPLE_DEV_CERT')
    cert_file.save('static/' + FOLDER + '/cert.p12')
    APPLE_DEV_CERT_BASE64 = base64.b64encode(open('static/' + FOLDER + '/cert.p12', 'rb').read()).decode('utf-8')
    APP_NAME = request.form.get('app_name')
    BUILDER_GITHUB_REPO_NAME = request.form.get('BUILDER_GITHUB_REPO_NAME')
    BUILDER_GITHUB_ORG_NAME = request.form.get('BUILDER_GITHUB_ORG_NAME')
    BUILDER_GITHUB_WORKFLOW_FILE_NAME = request.form.get('BUILDER_GITHUB_WORKFLOW_FILE_NAME')
    BUILDER_GITHUB_TOKEN = request.form.get('BUILDER_GITHUB_TOKEN')
    BUILDER_GITHUB_REF = request.form.get('BUILDER_GITHUB_REF')
    SERVER_URL = request.form.get('SERVER_URL')
    BASIC_AUTH_USERNAME = request.form.get('BASIC_AUTH_USERNAME')
    BASIC_AUTH_PASSWORD = request.form.get('BASIC_AUTH_PASSWORD')
    PROFILE_NAME = request.form.get('PROFILE_NAME')
    PROFILE_CERT_PASS = request.form.get('PROFILE_CERT_PASS')
    PROFILE_CERT_BASE64 = APPLE_DEV_CERT_BASE64
    PROFILE_ACCOUNT_NAME = request.form.get('PROFILE_ACCOUNT_NAME')
    PROFILE_ACCOUNT_PASS = request.form.get('PROFILE_ACCOUNT_PASS')



    with open('static/' + FOLDER + '/fly.toml', 'w') as f:
        f.write("""app = \"""" + APP_NAME + """\"
kill_signal = "SIGINT"
kill_timeout = 5
processes = []

[env]
  BASIC_AUTH_ENABLE = "true"
  BASIC_AUTH_PASSWORD = \"""" + BASIC_AUTH_PASSWORD + """\"
  BASIC_AUTH_USERNAME = \"""" + BASIC_AUTH_USERNAME + """\"
  BUILDER_GITHUB_ENABLE = "true"
  BUILDER_GITHUB_ORG_NAME = \"""" + BUILDER_GITHUB_ORG_NAME + """\"
  BUILDER_GITHUB_REPO_NAME = \"""" + BUILDER_GITHUB_REPO_NAME + """\"
  BUILDER_GITHUB_TOKEN = \"""" + BUILDER_GITHUB_TOKEN + """\"
  BUILDER_GITHUB_WORKFLOW_FILE_NAME = \"""" + BUILDER_GITHUB_WORKFLOW_FILE_NAME + """\"
  PROFILE_ACCOUNT_NAME = \"""" + PROFILE_ACCOUNT_NAME + """\"    
  PROFILE_ACCOUNT_PASS = \"""" + PROFILE_ACCOUNT_PASS + """\"
  PROFILE_CERT_BASE64 = \"""" + PROFILE_CERT_BASE64 + """\"
  PROFILE_CERT_PASS = \"""" + PROFILE_CERT_PASS + """\"
  PROFILE_NAME = \"""" + PROFILE_NAME + """\"
  PROFILE_PROV_BASE64 = ""
  REDIRECT_HTTPS = "true"
  SERVER_URL = \"""" + SERVER_URL + """\"
  
[experimental]
  allowed_public_ports = []
  auto_rollback = true

[[services]]
  http_checks = []
  internal_port = 8080
  processes = ["app"]
  protocol = "tcp"
  script_checks = []
  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "1s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"
""")
    thread = Thread(target=cleanup)
    thread.start()
    return send_file('static/' + FOLDER + '/fly.toml', as_attachment=True, download_name='fly.toml')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
