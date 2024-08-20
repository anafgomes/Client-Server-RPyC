import rpyc
import os
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import base64

# Classe que define o cliente para se conectar ao servidor RPyC
class Client(object):
    def __init__(self, conn):
        self.conn = conn  # Armazena a conexão com o servidor

    # Método que exibe uma notificação quando um novo arquivo está disponível
    def notify_event(self, filename):
        messagebox.showinfo("Notificação", f"Novo arquivo disponível: {filename}")

    # Método para fazer upload de um arquivo para o servidor
    def upload_file(self):
        filepath = filedialog.askopenfilename()  # Abre uma caixa de diálogo para escolher um arquivo
        if filepath:
            filename = os.path.basename(filepath)  # Obtém o nome do arquivo
            with open(filepath, 'rb') as file:
                content = file.read()  # Lê o conteúdo do arquivo
            # Serializa o conteúdo do arquivo em base64 para enviá-lo ao servidor
            serialized_content = {
                'data': base64.b64encode(content).decode('utf-8')
            }
            # Envia o arquivo para o servidor
            self.conn.root.upload_file(filename, serialized_content)
            messagebox.showinfo("Upload", f"Arquivo '{filename}' enviado com sucesso.")

    # Método para solicitar ao servidor a lista de arquivos disponíveis
    def list_available_files(self):
        files = self.conn.root.get_available_files()  # Solicita a lista de arquivos ao servidor
        if files:
            file_list = "\n".join(files)  # Concatena os nomes dos arquivos em uma única string
            messagebox.showinfo("Arquivos Disponíveis", f"Arquivos disponíveis:\n{file_list}")
        else:
            messagebox.showinfo("Arquivos Disponíveis", "Nenhum arquivo disponível.")

    # Método para fazer download de um arquivo do servidor
    def download_file(self):
        filename = simpledialog.askstring("Download", "Digite o nome do arquivo:")  # Solicita o nome do arquivo ao usuário
        if filename:
            result = self.conn.root.download_file(filename)  # Solicita o arquivo ao servidor
            if result:
                content = base64.b64decode(result['data'])  # Decodifica o conteúdo do arquivo
                # Abre uma caixa de diálogo para escolher onde salvar o arquivo baixado
                filepath = filedialog.asksaveasfilename(initialfile=result['filename'], filetypes=(("Todos os arquivos", "*.*"),))
                with open(filepath, 'wb') as file:
                    file.write(content)  # Salva o arquivo
                messagebox.showinfo("Download", f"Arquivo '{result['filename']}' baixado com sucesso.")
            else:
                messagebox.showerror("Download", f"Arquivo '{filename}' não encontrado.")

    # Método para registrar interesse em um arquivo no servidor
    def register_interest(self):
        filename = simpledialog.askstring("Registro de Interesse", "Digite o nome do arquivo:")  # Solicita o nome do arquivo ao usuário
        if filename:
            duration = simpledialog.askinteger("Registro de Interesse", "Digite a duração em segundos:")  # Solicita a duração do interesse
            if duration:
                # Registra o interesse no servidor com o nome do arquivo e a duração
                self.conn.root.register_interest(filename, duration)
                messagebox.showinfo("Registro de Interesse", f"Registro de interesse para o arquivo '{filename}' realizado com sucesso.")

    # Método para cancelar o interesse em um arquivo no servidor
    def cancel_interest(self):
        filename = simpledialog.askstring("Cancelamento de Interesse", "Digite o nome do arquivo:")  # Solicita o nome do arquivo ao usuário
        if filename:
            self.conn.root.cancel_interest(filename)  # Cancela o interesse no servidor
            messagebox.showinfo("Cancelamento de Interesse", f"Cancelamento de interesse para o arquivo '{filename}' realizado com sucesso.")

if __name__ == "__main__":
    conn = rpyc.connect("localhost", 18812)  # Conecta ao servidor RPyC rodando no localhost e porta 18812
    client = Client(conn)  # Cria uma instância do cliente

    root = tk.Tk()

    # Adiciona botões à interface gráfica do cliente, cada um vinculado a um método específico
    upload_button = tk.Button(root, text="Upload", command=client.upload_file)
    upload_button.pack()

    list_button = tk.Button(root, text="Listar Arquivos", command=client.list_available_files)
    list_button.pack()

    download_button = tk.Button(root, text="Download", command=client.download_file)
    download_button.pack()

    register_button = tk.Button(root, text="Registrar Interesse", command=client.register_interest)
    register_button.pack()

    cancel_button = tk.Button(root, text="Cancelar Interesse", command=client.cancel_interest)
    cancel_button.pack()

    root.geometry("400x300")  # Define o tamanho da janela principal
    root.mainloop()  # Inicia o loop principal da interface gráfica