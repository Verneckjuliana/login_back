from http.server import SimpleHTTPRequestHandler
import socketserver
import os 
from urllib.parse import parse_qs, urlparse
import hashlib
from database  import conectar

conexao = conectar()

class MyHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try: 
            with open(os.path.join(path, 'index.html'),'r',encoding='utf-8') as f:
                self.send_response(200)
                self.send_header('Content-type','text/html; charset=UTF-8')
                self.end_headers()
                self.wfile.write(f.read().encode('utf-8'))
                f.close()
            return None
        except FileNotFoundError:
            pass

        return super().list_directory(path)
    
    def do_GET(self):
        if self.path =='/login':
            try:
                with open(os.path.join(os.getcwd(),'login.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404,"File not found")
        elif self.path == '/login_failed':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8") 
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'login.html'), 'r', encoding='utf-8') as login_file:
                content = login_file.read()

            mensagem = "Login e/ou senha incorreta. Tente novamente."
            content = content.replace('<!-- Mensagem de erro será inserida aqui -->',
                                      f'<div class="error-message">{mensagem}</div>')
            
            self.wfile.write(content.encode('utf-8'))
            
        elif self.path.startswith('/cadastro'):
            query_params = parse_qs(urlparse(self.path).query)
            login = query_params.get('login', [''])[0]
            senha = query_params.get('senha', [''])[0]

            welcome_message = f'Olá {login}, seja bem-vindo!'

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastro.html'), 'r', encoding='utf-8') as cadastro_file:
                content = cadastro_file.read()

            content = content.replace('{login}', login)
            content = content.replace('{senha}', senha)
            content = content.replace('{welcome_message}', welcome_message)

            self.wfile.write(content.encode('utf-8'))

            return
        
        elif self.path == '/turmas':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open('turmas.html', 'r', encoding='utf-8') as file:
                content = file.read()

            self.wfile.write(content.encode('utf-8'))

        elif self.path == '/atividades':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open('atividades.html', 'r', encoding='utf-8') as file:
                content = file.read()

            self.wfile.write(content.encode('utf-8'))

        elif self.path == '/professor':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open('professor.html', 'r', encoding='utf-8') as file:
                content = file.read()

            self.wfile.write(content.encode('utf-8'))

        elif self.path == '/atividadesTurma':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open('atv_turmas.html', 'r', encoding='utf-8') as file:
                content = file.read()

            self.wfile.write(content.encode('utf-8'))

        else: 
            super().do_GET()

    def usuario_existente(self, login, senha):
        cursor = conexao.cursor()
        cursor.execute("SELECT senha FROM dados_login WHERE login = %s", (login,))
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            senha_hash = hashlib.sha3_256(senha.encode('utf-8')).hexdigest()
            return senha_hash == resultado[0]
        
        return False
    
    def adicionar_usuario(self, login, senha, nome):
        cursor = conexao.cursor()

        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        cursor.execute("INSERT INTO dados_login(login, senha, nome) VALUES (%s, %s, %s)", (login, senha_hash, nome))

        conexao.commit()

        cursor.close()
    
    def remover_ultima_linha(self, arquivo):
        print("Vou excluir a ultima linha")
        with open(arquivo, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open(arquivo, 'w', encoding='utf-8') as file:
            file.writelines(lines[:-1])

    def do_POST(self):
        if self.path == '/enviar_login':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]

            if self.usuario_existente(login, senha):
                with open(os.path.join(os.getcwd(),'pgresposta.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                cursor = conexao.cursor()
                cursor.execute("SELECT login FROM dados_login WHERE login = %s", (login,))
                resultado = cursor.fetchone()

                if resultado:
                    self.send_response(302)
                    self.send_header('Location', '/login_failed')
                    self.end_headers()
                    cursor.close()
                    return
                else: 
                    self.send_response(302)
                    self.send_header("Location", f'/cadastro?login={login}&senha={senha}')
                    self.end_headers()
                    cursor.close()
                    return


        elif self.path.startswith('/confirmar_cadastro'):
                            
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length).decode('utf-8')
                    form_data = parse_qs(body, keep_blank_values=True)

                    login = form_data.get('email', [''])[0]
                    senha = form_data.get('senha', [''])[0]
                    nome= form_data.get('nome', [''])[0]     

                    self.adicionar_usuario(login, senha, nome)

                    with open(os.path.join(os.getcwd(), 'pgresposta.html'), 'rb') as file:
                        content = file.read().decode('utf-8')

                    content = content.replace('{login}', login)
                    content = content.replace('{nome}', nome)

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))                    

        elif self.path == '/cad_turma':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            codigo = form_data.get('codigo', [''])[0]
            descricao = form_data.get('descricao', [''])[0]

            with open('dados_turma.txt', 'a', encoding='utf-8') as file:
                file.write(f"{codigo};{descricao}\n")

            with open(os.path.join(os.getcwd(),'resposta.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))


        elif self.path == '/cad_atividade':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            codigo = form_data.get('codigo', [''])[0]
            descricao = form_data.get('descricao', [''])[0]

            with open('dados_atividade.txt', 'a', encoding='utf-8') as file:
                file.write(f"{codigo};{descricao}\n")

            with open(os.path.join(os.getcwd(),'resposta.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path == '/cad_professor':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            login = form_data.get('email', [''])[0]
            turma = form_data.get('turma', [''])[0]

            with open('dados_login_turma.txt', 'a', encoding='utf-8') as file:
                file.write(f"{login};{turma}\n")

            with open(os.path.join(os.getcwd(),'resposta.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path == '/atividadesTurma':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            turma = form_data.get('turma', [''])[0]
            atividade = form_data.get('atividade', [''])[0]

            with open('atividades.txt', 'a', encoding='utf-8') as file:
                file.write(f"{turma};{atividade}\n")

            with open(os.path.join(os.getcwd(),'resposta.html'),'r',encoding='utf-8')as login_file:
                    content = login_file.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
           
        else:
           super(MyHandler, self).do_POST

endereco_ip = "0.0.0.0"

porta = 8000

with socketserver.TCPServer((endereco_ip,porta),MyHandler) as httpd:
    print(f'Servidor iniciado em {endereco_ip} na porta {porta}')
    httpd.serve_forever()
