import rpyc
import os
import time
import base64
from rpyc.utils.server import ThreadedServer

# Função para listar todos os arquivos em um diretório especificado
def get_files_in_folder(folder_path):
    files = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            files.append(file_name)
    return files

# Classe que define o serviço do servidor de arquivos usando RPyC
class FileServer(rpyc.Service):
    def __init__(self):
        self.files = {}  # Dicionário para armazenar os arquivos disponíveis
        self.interests = {}  # Dicionário para armazenar os interesses dos clientes

    # Método exposto que permite o upload de um arquivo do cliente para o servidor
    def exposed_upload_file(self, filename, content):
        print(f"Recebendo arquivo: {filename}")
        serialized_content = content
        # Decodifica o conteúdo do arquivo que foi serializado em base64
        decoded_content = base64.b64decode(serialized_content['data'])
        
        # Salva o arquivo no diretório 'arquivos'
        filepath = os.path.join('arquivos', filename)
        with open(filepath, 'wb') as file:
            file.write(decoded_content)
        
        print(f"Arquivo salvo em: {filepath}")
        # Verifica se há clientes interessados no arquivo e os notifica
        self.check_interests(filename)

    # Método exposto que retorna a lista de arquivos disponíveis no servidor
    def exposed_get_available_files(self):
        folder_path = 'arquivos'
        file_names = get_files_in_folder(folder_path)
        print(f"Arquivos disponíveis: {file_names}")
        return file_names

    # Método exposto que permite o download de um arquivo pelo cliente
    def exposed_download_file(self, filename):
        filepath = os.path.join('arquivos', filename)
        print(f"Tentando baixar o arquivo: {filepath}")
        if os.path.exists(filepath):
            with open(filepath, 'rb') as file:
                return {
                    'data': base64.b64encode(file.read()).decode('utf-8'),
                    'filename': filename
                }
        else:
            print(f"Arquivo não encontrado: {filepath}")
            return None

    # Método exposto que permite ao cliente registrar interesse em um arquivo por um determinado tempo
    def exposed_register_interest(self, filename, duration):
        expiration_time = time.time() + duration
        if filename in self.interests:
            self.interests[filename].append(expiration_time)
        else:
            self.interests[filename] = [expiration_time]

    # Método exposto que permite ao cliente cancelar o interesse em um arquivo
    def exposed_cancel_interest(self, filename):
        if filename in self.interests:
            del self.interests[filename]

    # Método interno que verifica se há clientes interessados em um arquivo e os notifica
    def check_interests(self, filename):
        if filename in self.interests:
            current_time = time.time()
            active_interests = [t for t in self.interests[filename] if current_time <= t]
            if active_interests:
                # Notificar os clientes interessados
                print(f"Notificando clientes sobre o arquivo: {filename}")
            self.interests[filename] = active_interests

if __name__ == "__main__":
    # Configura e inicia o servidor RPyC
    t = ThreadedServer(FileServer, port=18812)
    print("O servidor RPyC está rodando.")
    t.start()