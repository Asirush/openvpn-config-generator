import os
import subprocess
import tempfile
import tarfile
from flask import Flask, request, render_template, send_file, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def run_command(command, env=None, cwd=None):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=cwd)
    if result.returncode != 0:
        raise Exception(f"Command failed: {command}\n{result.stderr.decode('utf-8')}")
    return result.stdout.decode('utf-8')

def setup_easy_rsa(easy_rsa_dir):
    os.makedirs(easy_rsa_dir, exist_ok=True)
    run_command(f'cp -r /usr/share/easy-rsa/* {easy_rsa_dir}')
    run_command('./easyrsa init-pki', cwd=easy_rsa_dir)
    run_command('echo -ne "\\n" | ./easyrsa build-ca nopass', cwd=easy_rsa_dir)
    run_command('./easyrsa gen-dh', cwd=easy_rsa_dir)
    env = os.environ.copy()
    env['EASYRSA_BATCH'] = '1'
    env['EASYRSA_REQ_CN'] = 'server'
    run_command('./easyrsa gen-req server nopass', env=env, cwd=easy_rsa_dir)
    run_command('./easyrsa sign-req server server', env=env, cwd=easy_rsa_dir)
    run_command(f'openvpn --genkey --secret {os.path.join(easy_rsa_dir, "ta.key")}')

def read_pem_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def generate_server_config(easy_rsa_dir, ip, port, proto, dev):
    server_conf = f"""
port {port}
proto {proto}
dev {dev}
remote {ip}
server 10.8.0.0 255.255.255.0
ifconfig-pool-persist ipp.txt
keepalive 10 120
cipher AES-256-CBC
user nobody
group nogroup
persist-key
persist-tun
status openvpn-status.log
log-append /var/log/openvpn.log
verb 3

<ca>
{read_pem_file(os.path.join(easy_rsa_dir, 'pki/ca.crt'))}
</ca>
<cert>
{read_pem_file(os.path.join(easy_rsa_dir, 'pki/issued/server.crt'))}
</cert>
<key>
{read_pem_file(os.path.join(easy_rsa_dir, 'pki/private/server.key'))}
</key>
<dh>
{read_pem_file(os.path.join(easy_rsa_dir, 'pki/dh.pem'))}
</dh>
<tls-auth>
{read_pem_file(os.path.join(easy_rsa_dir, 'ta.key'))}
</tls-auth>
"""
    server_conf_path = os.path.join(easy_rsa_dir, 'server.conf')
    with open(server_conf_path, 'w') as f:
        f.write(server_conf)
    return server_conf_path

def parse_server_config(server_conf_path):
    config = {}
    with open(server_conf_path, 'r') as f:
        lines = f.readlines()
        inside_block = None
        block_content = []

        for line in lines:
            if line.startswith('<ca>'):
                inside_block = 'ca'
                block_content = []
            elif line.startswith('<cert>'):
                inside_block = 'cert'
                block_content = []
            elif line.startswith('<key>'):
                inside_block = 'key'
                block_content = []
            elif line.startswith('<dh>'):
                inside_block = 'dh'
                block_content = []
            elif line.startswith('<tls-auth>'):
                inside_block = 'tls-auth'
                block_content = []
            elif line.startswith('</ca>') or line.startswith('</cert>') or line.startswith('</key>') or line.startswith('</dh>') or line.startswith('</tls-auth>'):
                config[inside_block] = ''.join(block_content).strip()
                inside_block = None
            elif inside_block:
                block_content.append(line)
            else:
                if ' ' in line:
                    key, value = line.split(' ', 1)
                    config[key.strip()] = value.strip()

    return config

def generate_client_config_from_server(server_conf_path, client_name):
    config = parse_server_config(server_conf_path)

    client_conf = f"""
client
dev {config['dev']}
proto {config['proto']}
remote {config['remote']} {config['port']}
resolv-retry infinite
nobind
user nobody
group nogroup
persist-key
persist-tun
ca [inline]
cert [inline]
key [inline]
tls-auth [inline] 1
cipher AES-256-CBC
verb 3

<ca>
{config['ca']}
</ca>
<cert>
{config['cert']}
</cert>
<key>
{config['key']}
</key>
<tls-auth>
{config['tls-auth']}
</tls-auth>
"""
    return client_conf

def create_tar_archive(files, output_path):
    with tarfile.open(output_path, 'w:gz') as tar:
        for file in files:
            tar.add(file, arcname=os.path.basename(file))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            easy_rsa_dir = os.path.join(tempdir, 'easy-rsa')
            setup_easy_rsa(easy_rsa_dir)
            server_ip = request.form['server_ip']
            port = request.form['port']
            proto = request.form['proto']
            dev = request.form['dev']
            server_conf_path = generate_server_config(easy_rsa_dir, server_ip, port, proto, dev)
            tar_output_path = os.path.join(tempdir, 'configurations.tar.gz')
            create_tar_archive([server_conf_path], tar_output_path)
            return send_file(tar_output_path, as_attachment=True)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))

@app.route('/generate_client_from_server', methods=['POST'])
def generate_client_from_server():
    try:
        server_conf_file = request.files['server_conf_file']
        client_name = request.form['client_name']

        with tempfile.TemporaryDirectory() as tempdir:
            server_conf_path = os.path.join(tempdir, 'server.conf')
            server_conf_file.save(server_conf_path)
            client_conf = generate_client_config_from_server(server_conf_path, client_name)

            client_conf_path = os.path.join(tempdir, f'{client_name}.ovpn')
            with open(client_conf_path, 'w') as f:
                f.write(client_conf)

            tar_output_path = os.path.join(tempdir, f'{client_name}_configurations.tar.gz')
            create_tar_archive([client_conf_path], tar_output_path)
            return send_file(tar_output_path, as_attachment=True)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
