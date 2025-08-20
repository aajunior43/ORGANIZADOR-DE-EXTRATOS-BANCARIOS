#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏦 Organizador de Extratos Bancários com Interface Gráfica
Powered by Gemini AI

Programa com interface gráfica moderna para organizar automaticamente
extratos bancários usando inteligência artificial.

Autor: Assistente IA
Versão: 2.0 GUI
"""

import os
import sys
import json
import shutil
import threading
import time
from pathlib import Path
from datetime import datetime
import re
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.font import Font

# Função para obter o diretório base (compatível com PyInstaller)
def get_base_path():
    """Obtém o diretório base do aplicativo (compatível com executável)"""
    if getattr(sys, 'frozen', False):
        # Executando como executável PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # Executando como script Python
        return os.path.dirname(os.path.abspath(__file__))

# Função para obter caminho de recursos (compatível com PyInstaller)
def get_resource_path(relative_path):
    """Obtém o caminho absoluto para recursos (compatível com executável)"""
    if getattr(sys, 'frozen', False):
        # Executando como executável PyInstaller
        base_path = sys._MEIPASS
    else:
        # Executando como script Python
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

# Importações para processamento de arquivos
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# ==================== CONFIGURAÇÕES ====================

# Mapeamento de meses
MES_NOMES = {
    1: "01_JANEIRO", 2: "02_FEVEREIRO", 3: "03_MARÇO", 4: "04_ABRIL",
    5: "05_MAIO", 6: "06_JUNHO", 7: "07_JULHO", 8: "08_AGOSTO",
    9: "09_SETEMBRO", 10: "10_OUTUBRO", 11: "11_NOVEMBRO", 12: "12_DEZEMBRO"
}

# Padrões de arquivos para processar
FILE_PATTERNS = ["*.pdf", "*.ofx"]

# ==================== CLASSE PRINCIPAL GUI ====================

class OrganizadorExtratosGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.check_dependencies()
        
    def setup_window(self):
        """Configura a janela principal"""
        self.root.title("🏦 Organizador de Extratos Bancários - Gemini AI")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Centraliza a janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
        # Configura o estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Cores personalizadas
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'success': '#F18F01',
            'background': '#F5F5F5',
            'text': '#2C3E50'
        }
        
    def setup_variables(self):
        """Inicializa variáveis"""
        self.api_keys = []  # Lista de chaves API
        self.current_api_index = 0  # Índice da chave atual
        
        # Diretórios compatíveis com executável
        self.app_data_dir = self.get_app_data_directory()
        self.base_directory = StringVar(value=os.getcwd())
        self.output_directory = StringVar(value="EXTRATOS_ORGANIZADOS")
        
        self.processing = False
        self.processing_log = []
        
        # Arquivos de configuração no diretório de dados do app
        self.checkpoint_file = os.path.join(self.app_data_dir, "processing_checkpoint.json")
        self.api_keys_file = os.path.join(self.app_data_dir, "api_keys.json")
        
        self.stats = {
            'total_files': 0,
            'success': 0,
            'errors': 0,
            'by_bank': {},
            'by_month': {}
        }
        
        # Carrega chaves salvas
        self.load_api_keys()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal com scroll
        main_frame = Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_frame = Frame(main_frame, bg=self.colors['background'])
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_font = Font(family="Arial", size=18, weight="bold")
        title_label = Label(title_frame, text="🏦 Organizador de Extratos Bancários", 
                           font=title_font, bg=self.colors['background'], 
                           fg=self.colors['primary'])
        title_label.pack()
        
        subtitle_label = Label(title_frame, text="Powered by Google Gemini AI", 
                              font=("Arial", 10), bg=self.colors['background'], 
                              fg=self.colors['text'])
        subtitle_label.pack()
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Aba 1: Configuração
        self.setup_config_tab()
        
        # Aba 2: Processamento
        self.setup_processing_tab()
        
        # Verifica se há checkpoint para retomar
        self.check_for_checkpoint()
        
        # Aba 3: Resultados
        self.setup_results_tab()
        
        # Frame de status na parte inferior
        self.setup_status_frame(main_frame)
        
    def setup_config_tab(self):
        """Configura a aba de configuração"""
        config_frame = Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(config_frame, text="⚙️ Configuração")
        
        # Seção API Keys
        api_section = LabelFrame(config_frame, text="🔑 Chaves da API do Gemini", 
                                font=("Arial", 12, "bold"), bg=self.colors['background'])
        api_section.pack(fill=X, padx=20, pady=10)
        
        Label(api_section, text="Gerencie suas chaves da API do Google Gemini:", 
              bg=self.colors['background']).pack(anchor=W, padx=10, pady=5)
        
        # Frame para adicionar nova chave
        add_key_frame = Frame(api_section, bg=self.colors['background'])
        add_key_frame.pack(fill=X, padx=10, pady=5)
        
        self.new_api_key = StringVar()
        self.api_entry = Entry(add_key_frame, textvariable=self.new_api_key, 
                              font=("Arial", 10), show="*", width=40)
        self.api_entry.pack(side=LEFT, fill=X, expand=True)
        
        Button(add_key_frame, text="Adicionar", command=self.add_api_key,
               bg=self.colors['success'], fg='white', font=("Arial", 9)).pack(side=RIGHT, padx=(5, 0))
        
        Button(add_key_frame, text="Obter Chave", command=self.open_api_url,
               bg=self.colors['primary'], fg='white', font=("Arial", 9)).pack(side=RIGHT, padx=(5, 0))
        
        # Lista de chaves existentes
        keys_list_frame = Frame(api_section, bg=self.colors['background'])
        keys_list_frame.pack(fill=X, padx=10, pady=(5, 10))
        
        Label(keys_list_frame, text="Chaves configuradas:", 
              bg=self.colors['background'], font=("Arial", 10, "bold")).pack(anchor=W)
        
        # Frame com scroll para lista de chaves
        list_container = Frame(keys_list_frame, bg=self.colors['background'])
        list_container.pack(fill=X, pady=5)
        
        self.keys_listbox = Listbox(list_container, height=4, font=("Arial", 9))
        keys_scrollbar = Scrollbar(list_container, orient=VERTICAL, command=self.keys_listbox.yview)
        self.keys_listbox.config(yscrollcommand=keys_scrollbar.set)
        
        self.keys_listbox.pack(side=LEFT, fill=X, expand=True)
        keys_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Botões de gerenciamento
        keys_buttons = Frame(keys_list_frame, bg=self.colors['background'])
        keys_buttons.pack(fill=X, pady=5)
        
        Button(keys_buttons, text="🧪 Testar Selecionada", command=self.test_selected_api,
               bg=self.colors['secondary'], fg='white', font=("Arial", 9)).pack(side=LEFT, padx=(0, 5))
        
        Button(keys_buttons, text="🧪 Testar Todas", command=self.test_all_apis,
               bg=self.colors['primary'], fg='white', font=("Arial", 9)).pack(side=LEFT, padx=(0, 5))
        
        Button(keys_buttons, text="🗑️ Remover", command=self.remove_selected_api,
               bg=self.colors['secondary'], fg='white', font=("Arial", 9)).pack(side=LEFT, padx=(0, 5))
        
        self.api_status_label = Label(keys_buttons, text="", 
                                     bg=self.colors['background'], font=("Arial", 9))
        self.api_status_label.pack(side=RIGHT)
        
        # Atualiza a lista
        self.update_keys_display()
        
        # Seção Diretórios
        dir_section = LabelFrame(config_frame, text="📁 Diretórios", 
                                font=("Arial", 12, "bold"), bg=self.colors['background'])
        dir_section.pack(fill=X, padx=20, pady=10)
        
        # Aviso de segurança
        security_frame = Frame(dir_section, bg='#e8f5e8', relief=RIDGE, bd=1)
        security_frame.pack(fill=X, padx=10, pady=(10, 5))
        
        Label(security_frame, text="🛡️ SEGURANÇA GARANTIDA", 
              bg='#e8f5e8', fg='#2d5a2d', font=("Arial", 10, "bold")).pack(pady=2)
        Label(security_frame, text="• Arquivos originais NUNCA são movidos ou alterados", 
              bg='#e8f5e8', fg='#2d5a2d', font=("Arial", 9)).pack(anchor=W, padx=5)
        Label(security_frame, text="• Apenas CÓPIAS são organizadas na nova estrutura", 
              bg='#e8f5e8', fg='#2d5a2d', font=("Arial", 9)).pack(anchor=W, padx=5)
        Label(security_frame, text="• Verificação de integridade em cada cópia", 
              bg='#e8f5e8', fg='#2d5a2d', font=("Arial", 9)).pack(anchor=W, padx=5, pady=(0, 2))
        
        # Diretório de entrada
        Label(dir_section, text="Diretório dos extratos:", 
              bg=self.colors['background']).pack(anchor=W, padx=10, pady=(10, 5))
        
        input_frame = Frame(dir_section, bg=self.colors['background'])
        input_frame.pack(fill=X, padx=10, pady=5)
        
        Entry(input_frame, textvariable=self.base_directory, 
              font=("Arial", 10), state='readonly').pack(side=LEFT, fill=X, expand=True)
        
        Button(input_frame, text="Selecionar", command=self.select_input_directory,
               bg=self.colors['success'], fg='white').pack(side=RIGHT, padx=(5, 0))
        
        # Diretório de saída
        Label(dir_section, text="Nome da pasta organizada:", 
              bg=self.colors['background']).pack(anchor=W, padx=10, pady=(10, 5))
        
        Entry(dir_section, textvariable=self.output_directory, 
              font=("Arial", 10)).pack(fill=X, padx=10, pady=(5, 10))
        
        # Seção Arquivos Encontrados
        files_section = LabelFrame(config_frame, text="📄 Arquivos Encontrados", 
                                  font=("Arial", 12, "bold"), bg=self.colors['background'])
        files_section.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        scan_frame = Frame(files_section, bg=self.colors['background'])
        scan_frame.pack(fill=X, padx=10, pady=10)
        
        Button(scan_frame, text="🔍 Escanear Arquivos", command=self.scan_files,
               bg=self.colors['primary'], fg='white', font=("Arial", 11, "bold")).pack(side=LEFT)
        
        self.files_count_label = Label(scan_frame, text="Nenhum arquivo escaneado ainda", 
                                      bg=self.colors['background'], font=("Arial", 10))
        self.files_count_label.pack(side=RIGHT)
        
        # Lista de arquivos
        self.files_listbox = Listbox(files_section, height=8, font=("Arial", 9))
        scrollbar = Scrollbar(files_section, orient=VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        
        self.files_listbox.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side=RIGHT, fill=Y, padx=(0, 10), pady=(0, 10))
        
    def setup_processing_tab(self):
        """Configura a aba de processamento"""
        process_frame = Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(process_frame, text="🚀 Processamento")
        
        # Controles de processamento
        control_frame = Frame(process_frame, bg=self.colors['background'])
        control_frame.pack(fill=X, padx=20, pady=20)
        
        self.start_button = Button(control_frame, text="🚀 Iniciar Organização", 
                                  command=self.start_processing,
                                  bg=self.colors['success'], fg='white', 
                                  font=("Arial", 14, "bold"), height=2)
        self.start_button.pack(side=LEFT, padx=(0, 10))
        
        self.resume_button = Button(control_frame, text="▶️ Retomar", 
                                   command=self.resume_processing,
                                   bg=self.colors['primary'], fg='white', 
                                   font=("Arial", 14, "bold"), height=2, state=DISABLED)
        self.resume_button.pack(side=LEFT, padx=(0, 10))
        
        self.stop_button = Button(control_frame, text="⏹️ Parar", 
                                 command=self.stop_processing,
                                 bg=self.colors['secondary'], fg='white', 
                                 font=("Arial", 14, "bold"), height=2, state=DISABLED)
        self.stop_button.pack(side=LEFT)
        
        # Barra de progresso
        progress_frame = LabelFrame(process_frame, text="📊 Progresso", 
                                   font=("Arial", 12, "bold"), bg=self.colors['background'])
        progress_frame.pack(fill=X, padx=20, pady=10)
        
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(padx=10, pady=10)
        
        self.progress_label = Label(progress_frame, text="Aguardando início...", 
                                   bg=self.colors['background'], font=("Arial", 10))
        self.progress_label.pack(pady=(0, 10))
        
        # Log de processamento
        log_frame = LabelFrame(process_frame, text="📋 Log de Processamento", 
                              font=("Arial", 12, "bold"), bg=self.colors['background'])
        log_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                 font=("Consolas", 9), 
                                                 bg='#1e1e1e', fg='#ffffff')
        self.log_text.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
    def setup_results_tab(self):
        """Configura a aba de resultados"""
        results_frame = Frame(self.notebook, bg=self.colors['background'])
        self.notebook.add(results_frame, text="📊 Resultados")
        
        # Estatísticas
        stats_frame = LabelFrame(results_frame, text="📈 Estatísticas", 
                                font=("Arial", 12, "bold"), bg=self.colors['background'])
        stats_frame.pack(fill=X, padx=20, pady=20)
        
        self.stats_text = Text(stats_frame, height=8, font=("Arial", 10), 
                              bg='white', state=DISABLED)
        self.stats_text.pack(fill=X, padx=10, pady=10)
        
        # Ações
        actions_frame = LabelFrame(results_frame, text="🔧 Ações", 
                                  font=("Arial", 12, "bold"), bg=self.colors['background'])
        actions_frame.pack(fill=X, padx=20, pady=10)
        
        actions_buttons = Frame(actions_frame, bg=self.colors['background'])
        actions_buttons.pack(padx=10, pady=10)
        
        Button(actions_buttons, text="📁 Abrir Pasta Organizada", 
               command=self.open_output_folder,
               bg=self.colors['primary'], fg='white', font=("Arial", 10)).pack(side=LEFT, padx=(0, 10))
        
        Button(actions_buttons, text="📋 Salvar Log", 
               command=self.save_log,
               bg=self.colors['secondary'], fg='white', font=("Arial", 10)).pack(side=LEFT, padx=(0, 10))
        
        Button(actions_buttons, text="🔄 Novo Processamento", 
               command=self.reset_processing,
               bg=self.colors['success'], fg='white', font=("Arial", 10)).pack(side=LEFT, padx=(0, 10))
        
        Button(actions_buttons, text="📂 Limpar Checkpoint", 
               command=self.clear_checkpoint,
               bg=self.colors['secondary'], fg='white', font=("Arial", 10)).pack(side=LEFT)
        
    def setup_status_frame(self, parent):
        """Configura a barra de status"""
        status_frame = Frame(parent, bg=self.colors['primary'], height=30)
        status_frame.pack(fill=X, side=BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = Label(status_frame, text="Pronto para começar", 
                                 bg=self.colors['primary'], fg='white', 
                                 font=("Arial", 9))
        self.status_label.pack(side=LEFT, padx=10, pady=5)
        
        # Indicador de dependências
        self.deps_label = Label(status_frame, text="Verificando dependências...", 
                               bg=self.colors['primary'], fg='white', 
                               font=("Arial", 9))
        self.deps_label.pack(side=RIGHT, padx=10, pady=5)
        
    def check_dependencies(self):
        """Verifica se as dependências estão instaladas"""
        missing = []
        
        if PyPDF2 is None:
            missing.append("PyPDF2")
        if genai is None:
            missing.append("google-generativeai")
            
        if missing:
            self.deps_label.config(text=f"❌ Faltam: {', '.join(missing)}", fg='#ffcccc')
            messagebox.showerror("Dependências Faltando", 
                                f"Instale as dependências faltando:\n\npip install {' '.join(missing)}")
        else:
            self.deps_label.config(text="✅ Dependências OK", fg='#ccffcc')
            
    def open_api_url(self):
        """Abre a URL para obter a chave da API"""
        import webbrowser
        webbrowser.open("https://makersuite.google.com/app/apikey")
        
    def add_api_key(self):
        """Adiciona uma nova chave API"""
        new_key = self.new_api_key.get().strip()
        if not new_key:
            messagebox.showerror("Erro", "Digite uma chave da API!")
            return
            
        if new_key in self.api_keys:
            messagebox.showwarning("Aviso", "Esta chave já foi adicionada!")
            return
            
        # Testa a chave antes de adicionar
        try:
            genai.configure(api_key=new_key)
            
            # Tenta diferentes modelos disponíveis
            models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            model_worked = False
            
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content("Responda apenas: OK")
                    
                    if response and response.text and "OK" in response.text:
                        model_worked = True
                        break
                except Exception as model_error:
                    continue  # Tenta próximo modelo
            
            if model_worked:
                self.api_keys.append(new_key)
                self.save_api_keys()
                self.update_keys_display()
                self.new_api_key.set("")
                messagebox.showinfo("Sucesso", f"✅ Chave adicionada e testada com sucesso!\nModelo usado: {model_name}")
                self.status_label.config(text=f"{len(self.api_keys)} chave(s) configurada(s)")
            else:
                messagebox.showerror("Erro", "Chave inválida ou modelos indisponíveis.\nVerifique se a chave está correta e se o Gemini está disponível na sua região.")
                
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                messagebox.showerror("Erro de API", "Modelo não encontrado.\nO Gemini pode não estar disponível na sua região.\nTente usar VPN ou aguarde disponibilidade.")
            elif "403" in error_msg:
                messagebox.showerror("Erro de API", "Chave API inválida ou sem permissões.\nVerifique se a chave está correta.")
            else:
                messagebox.showerror("Erro de API", f"Erro ao testar chave:\n{error_msg}")
            
    def remove_selected_api(self):
        """Remove a chave API selecionada"""
        selection = self.keys_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma chave para remover!")
            return
            
        index = selection[0]
        if messagebox.askyesno("Confirmar", "Deseja remover a chave selecionada?"):
            removed_key = self.api_keys.pop(index)
            self.save_api_keys()
            self.update_keys_display()
            
            # Ajusta o índice atual se necessário
            if self.current_api_index >= len(self.api_keys):
                self.current_api_index = 0
                
            messagebox.showinfo("Sucesso", "Chave removida com sucesso!")
            self.status_label.config(text=f"{len(self.api_keys)} chave(s) configurada(s)")
            
    def test_selected_api(self):
        """Testa a chave API selecionada"""
        selection = self.keys_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma chave para testar!")
            return
            
        index = selection[0]
        api_key = self.api_keys[index]
        
        try:
            genai.configure(api_key=api_key)
            
            # Tenta diferentes modelos disponíveis
            models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            model_worked = False
            
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content("Responda apenas: OK")
                    
                    if response and response.text and "OK" in response.text:
                        model_worked = True
                        break
                except Exception:
                    continue
            
            if model_worked:
                messagebox.showinfo("Sucesso", f"✅ Chave {index + 1} funcionando!\nModelo: {model_name}")
                self.api_status_label.config(text=f"Chave {index + 1}: ✅ OK")
            else:
                messagebox.showerror("Erro", f"Chave {index + 1}: Modelos indisponíveis")
                self.api_status_label.config(text=f"Chave {index + 1}: ❌ Erro")
        except Exception as e:
            messagebox.showerror("Erro de API", f"Chave {index + 1} falhou:\n{str(e)}")
            self.api_status_label.config(text=f"Chave {index + 1}: ❌ Falhou")
            
    def test_all_apis(self):
        """Testa todas as chaves API"""
        if not self.api_keys:
            messagebox.showwarning("Aviso", "Nenhuma chave configurada!")
            return
            
        working_keys = 0
        failed_keys = 0
        
        for i, api_key in enumerate(self.api_keys):
            try:
                genai.configure(api_key=api_key)
                
                # Tenta diferentes modelos disponíveis
                models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                model_worked = False
                
                for model_name in models_to_try:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content("Responda apenas: OK")
                        
                        if response and response.text and "OK" in response.text:
                            model_worked = True
                            break
                    except Exception:
                        continue
                
                if model_worked:
                    working_keys += 1
                else:
                    failed_keys += 1
            except Exception:
                failed_keys += 1
                
        result_msg = f"Resultado dos testes:\n\n"
        result_msg += f"✅ Chaves funcionando: {working_keys}\n"
        result_msg += f"❌ Chaves com problema: {failed_keys}\n"
        result_msg += f"📊 Total: {len(self.api_keys)} chaves"
        
        if working_keys > 0:
            messagebox.showinfo("Resultado dos Testes", result_msg)
        else:
            messagebox.showerror("Erro", result_msg + "\n\n⚠️ Nenhuma chave está funcionando!")
            
        self.api_status_label.config(text=f"{working_keys}/{len(self.api_keys)} OK")
            
    def select_input_directory(self):
        """Seleciona o diretório de entrada"""
        directory = filedialog.askdirectory(title="Selecione a pasta com os extratos")
        if directory:
            self.base_directory.set(directory)
            self.status_label.config(text=f"Diretório selecionado: {os.path.basename(directory)}")
            
    def scan_files(self):
        """Escaneia arquivos no diretório selecionado"""
        if not os.path.exists(self.base_directory.get()):
            messagebox.showerror("Erro", "Diretório não existe!")
            return
            
        self.files_listbox.delete(0, END)
        files_found = []
        
        for pattern in FILE_PATTERNS:
            extension = pattern[1:]  # Remove '*'
            for root, dirs, files in os.walk(self.base_directory.get()):
                for file in files:
                    if file.lower().endswith(extension):
                        full_path = os.path.join(root, file)
                        files_found.append(full_path)
                        
        files_found.sort()
        
        for file_path in files_found:
            rel_path = os.path.relpath(file_path, self.base_directory.get())
            self.files_listbox.insert(END, rel_path)
            
        count = len(files_found)
        self.files_count_label.config(text=f"{count} arquivos encontrados")
        self.status_label.config(text=f"Escaneamento concluído: {count} arquivos")
        
        return files_found
        
    def log_message(self, message, level="INFO"):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Cores por nível
        colors = {
            "INFO": "#ffffff",
            "SUCCESS": "#90EE90", 
            "WARNING": "#FFD700",
            "ERROR": "#FF6B6B"
        }
        
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, f"[{timestamp}] {message}\n")
        
        # Aplica cor à última linha
        line_start = self.log_text.index("end-2c linestart")
        line_end = self.log_text.index("end-2c lineend")
        
        tag_name = f"level_{level}_{timestamp}"
        self.log_text.tag_add(tag_name, line_start, line_end)
        self.log_text.tag_config(tag_name, foreground=colors.get(level, "#ffffff"))
        
        self.log_text.config(state=DISABLED)
        self.log_text.see(END)
        
        # Atualiza a interface
        self.root.update_idletasks()
        
    def start_processing(self):
        """Inicia o processamento em thread separada"""
        if self.processing:
            return
            
        # Validações
        if not self.api_keys:
            messagebox.showerror("Erro", "Configure pelo menos uma chave da API primeiro!")
            self.notebook.select(0)  # Vai para aba de configuração
            return
            
        files = self.scan_files()
        if not files:
            messagebox.showerror("Erro", "Nenhum arquivo encontrado para processar!")
            return
            
        # Limpa checkpoint anterior para novo processamento
        self.clear_checkpoint()
            
        # Configura interface para processamento
        self.processing = True
        self.start_button.config(state=DISABLED)
        self.resume_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        self.notebook.select(1)  # Vai para aba de processamento
        
        # Limpa log anterior
        self.log_text.config(state=NORMAL)
        self.log_text.delete(1.0, END)
        self.log_text.config(state=DISABLED)
        
        # Inicia thread de processamento
        self.processing_thread = threading.Thread(target=self.process_files, args=(files, 0))
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
    def stop_processing(self):
        """Para o processamento"""
        self.processing = False
        self.start_button.config(state=NORMAL)
        self.resume_button.config(state=NORMAL if self.has_checkpoint() else DISABLED)
        self.stop_button.config(state=DISABLED)
        self.log_message("❌ Processamento interrompido pelo usuário", "WARNING")
        self.log_message("💾 Checkpoint salvo - use 'Retomar' para continuar", "INFO")
        self.status_label.config(text="Processamento interrompido - checkpoint salvo")
        
    def process_files(self, files, start_index=0):
        """Processa os arquivos (executado em thread separada)"""
        try:
            if start_index == 0:
                self.log_message("🚀 Iniciando organização dos extratos bancários...", "INFO")
            else:
                self.log_message(f"▶️ Retomando processamento do arquivo {start_index + 1}...", "INFO")
                
            self.log_message(f"📁 Diretório base: {self.base_directory.get()}", "INFO")
            self.log_message(f"📁 Diretório de saída: {self.output_directory.get()}", "INFO")
            self.log_message(f"📄 Total de arquivos: {len(files)}", "INFO")
            self.log_message(f"📄 Iniciando do arquivo: {start_index + 1}", "INFO")
            self.log_message("", "INFO")
            self.log_message("🛡️ SEGURANÇA: Todos os arquivos originais serão preservados", "SUCCESS")
            self.log_message("📋 OPERAÇÃO: Apenas cópias serão organizadas na nova estrutura", "INFO")
            self.log_message("", "INFO")
            
            # Configura Gemini com a primeira chave disponível
            if not self.api_keys:
                raise Exception("Nenhuma chave API configurada")
            
            self.current_api_index = 0
            genai.configure(api_key=self.api_keys[self.current_api_index])
            
            # Tenta diferentes modelos disponíveis
            models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            model = None
            
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    # Testa o modelo com uma requisição simples
                    test_response = model.generate_content("OK")
                    if test_response:
                        self.log_message(f"🤖 Modelo ativo: {model_name}", "INFO")
                        break
                except Exception:
                    continue
            
            if not model:
                raise Exception("Nenhum modelo Gemini disponível")
            
            self.log_message(f"🔑 Usando rotação de {len(self.api_keys)} chave(s) API", "INFO")
            
            # Carrega estatísticas do checkpoint se existir
            checkpoint_data = self.load_checkpoint()
            if checkpoint_data and start_index > 0:
                self.stats = checkpoint_data.get('stats', {
                    'total_files': len(files),
                    'success': 0,
                    'errors': 0,
                    'by_bank': {},
                    'by_month': {}
                })
            else:
                self.stats = {
                    'total_files': len(files),
                    'success': 0,
                    'errors': 0,
                    'by_bank': {},
                    'by_month': {}
                }
            
            # Processa cada arquivo a partir do índice especificado
            for i in range(start_index, len(files)):
                if not self.processing:
                    # Salva checkpoint antes de parar
                    self.save_checkpoint(files, i, self.stats)
                    break
                    
                # Atualiza progresso
                progress = (i / len(files)) * 100
                self.progress_var.set(progress)
                self.progress_label.config(text=f"Processando arquivo {i+1}/{len(files)}")
                
                file_path = files[i]
                file_name = os.path.basename(file_path)
                self.log_message(f"[{i+1}/{len(files)}] 🔍 Processando: {file_name}", "INFO")
                
                try:
                    # Salva checkpoint antes de processar cada arquivo
                    self.save_checkpoint(files, i, self.stats)
                    
                    # Processa arquivo individual
                    success = self.process_single_file(file_path, model)
                    
                    if success:
                        self.stats['success'] += 1
                    else:
                        self.stats['errors'] += 1
                        
                except Exception as e:
                    self.log_message(f"❌ Erro ao processar {file_name}: {str(e)}", "ERROR")
                    self.stats['errors'] += 1
                    # Salva checkpoint mesmo com erro
                    self.save_checkpoint(files, i + 1, self.stats)
                
                # Pausa de 10 segundos entre arquivos
                if i < len(files) - 1 and self.processing:
                    self.log_message("⏱️ Aguardando 10 segundos antes do próximo arquivo...", "INFO")
                    for second in range(10):
                        if not self.processing:
                            break
                        time.sleep(1)
                        
            # Finaliza processamento
            if self.processing:
                self.progress_var.set(100)
                self.progress_label.config(text="Processamento concluído!")
                self.log_message("", "INFO")
                self.log_message("🎉 Organização concluída com sucesso!", "SUCCESS")
                self.log_message("", "INFO")
                self.log_message("🛡️ CONFIRMAÇÃO DE SEGURANÇA:", "SUCCESS")
                self.log_message("   ✅ Todos os arquivos originais estão INTACTOS", "SUCCESS")
                self.log_message("   ✅ Apenas cópias foram organizadas", "SUCCESS")
                self.log_message("   ✅ Nenhum documento original foi alterado", "SUCCESS")
                self.show_final_stats()
                self.clear_checkpoint()  # Remove checkpoint após conclusão
                self.notebook.select(2)  # Vai para aba de resultados
                
        except Exception as e:
            self.log_message(f"❌ Erro crítico: {str(e)}", "ERROR")
            # Salva checkpoint em caso de erro crítico
            try:
                current_index = locals().get('i', start_index)
                self.save_checkpoint(files, current_index, self.stats)
                self.log_message("💾 Checkpoint salvo devido ao erro", "INFO")
            except:
                pass
            messagebox.showerror("Erro Crítico", f"Erro durante processamento:\n{str(e)}\n\nCheckpoint salvo - use 'Retomar' para continuar")
            
        finally:
            # Restaura interface
            self.processing = False
            self.start_button.config(state=NORMAL)
            self.resume_button.config(state=NORMAL if self.has_checkpoint() else DISABLED)
            self.stop_button.config(state=DISABLED)
            
    def process_single_file(self, file_path, model):
        """Processa um único arquivo"""
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Extrai conteúdo
        if file_ext == '.pdf':
            content = self.extract_text_from_pdf(file_path)
            file_type = 'PDF'
        elif file_ext == '.ofx':
            content = self.extract_text_from_ofx(file_path)
            file_type = 'OFX'
        else:
            self.log_message(f"⚠️ Tipo de arquivo não suportado: {file_ext}", "WARNING")
            return False
            
        if not content:
            self.log_message(f"❌ Não foi possível extrair conteúdo", "ERROR")
            return False
            
        # Analisa com IA
        analysis = self.analyze_file_with_gemini(content, file_name, model)
        analysis['file_type'] = file_type
        
        # Cria estrutura de pastas
        destination_folder = self.create_organized_structure(analysis)
        
        # Copia arquivo
        copied_path = self.copy_file_to_destination(file_path, destination_folder, file_name)
        
        if copied_path:
            # Atualiza estatísticas
            banco = analysis['banco']
            mes_ano = f"{analysis['mes']:02d}/{analysis['ano']}"
            tipo_conta = analysis['tipo_conta']
            formato = analysis['file_type']
            
            self.stats['by_bank'][banco] = self.stats['by_bank'].get(banco, 0) + 1
            self.stats['by_month'][mes_ano] = self.stats['by_month'].get(mes_ano, 0) + 1
            
            # Adiciona estatísticas por tipo de conta e formato
            if 'by_account_type' not in self.stats:
                self.stats['by_account_type'] = {}
            if 'by_format' not in self.stats:
                self.stats['by_format'] = {}
                
            self.stats['by_account_type'][tipo_conta] = self.stats['by_account_type'].get(tipo_conta, 0) + 1
            self.stats['by_format'][formato] = self.stats['by_format'].get(formato, 0) + 1
            
            self.log_message(f"✅ Organizado: {banco} - {mes_ano} - {tipo_conta} - {formato}", "SUCCESS")
            return True
        else:
            return False
            
    def extract_text_from_pdf(self, file_path):
        """Extrai texto de arquivo PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                max_pages = min(3, len(pdf_reader.pages))
                for page_num in range(max_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                return text[:2000]
        except Exception as e:
            self.log_message(f"⚠️ Erro ao ler PDF: {e}", "WARNING")
            return None
            
    def extract_text_from_ofx(self, file_path):
        """Extrai texto de arquivo OFX"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read(2000)
                return content
        except Exception as e:
            self.log_message(f"⚠️ Erro ao ler OFX: {e}", "WARNING")
            return None
            
    def get_next_api_key(self):
        """Obtém a próxima chave API na rotação"""
        if not self.api_keys:
            return None
            
        # Rotaciona para a próxima chave
        self.current_api_index = (self.current_api_index + 1) % len(self.api_keys)
        return self.api_keys[self.current_api_index]
        
    def analyze_file_with_gemini(self, file_content, file_name, model):
        """Analisa o conteúdo do arquivo usando Gemini AI com rotação de chaves"""
        prompt = f"""
        Analise este extrato bancário e retorne APENAS um JSON válido:
        
        {{
            "banco": "CAIXA" ou "BANCO_DO_BRASIL",
            "mes": número do mês (1-12),
            "ano": ano com 4 dígitos,
            "tipo_conta": "corrente", "poupanca" ou "investimento"
        }}
        
        Regras:
        - Se for Caixa Econômica Federal, use "CAIXA"
        - Se for Banco do Brasil, use "BANCO_DO_BRASIL"
        - Para investimentos, fundos, aplicações, use "investimento"
        - Para conta corrente, use "corrente"
        - Para poupança, use "poupanca"
        
        Nome do arquivo: {file_name}
        Conteúdo: {file_content[:1500]}
        
        Retorne APENAS o JSON:
        """
        
        max_retries = 3
        keys_tried = set()
        
        for attempt in range(max_retries):
            if not self.processing:
                break
                
            try:
                current_key_index = self.current_api_index + 1
                self.log_message(f"   🤖 Tentativa {attempt + 1}/{max_retries} (Chave {current_key_index}/{len(self.api_keys)})...", "INFO")
                
                response = model.generate_content(prompt)
                result_text = response.text.strip()
                
                # Remove marcadores de código
                result_text = result_text.replace('```json', '').replace('```', '').strip()
                
                # Parse JSON
                result = json.loads(result_text)
                
                # Validação
                required_keys = ['banco', 'mes', 'ano', 'tipo_conta']
                if all(key in result for key in required_keys):
                    self.log_message(f"   ✅ Análise IA bem-sucedida (Chave {current_key_index})", "SUCCESS")
                    return result
                else:
                    raise ValueError("JSON incompleto")
                    
            except Exception as e:
                current_key_index = self.current_api_index + 1
                self.log_message(f"   ⚠️ Tentativa {attempt + 1} falhou (Chave {current_key_index}): {e}", "WARNING")
                
                # Marca esta chave como tentada
                keys_tried.add(self.current_api_index)
                
                if attempt < max_retries - 1:
                    # Tenta próxima chave se disponível
                    if len(keys_tried) < len(self.api_keys):
                        next_key = self.get_next_api_key()
                        if next_key:
                            try:
                                genai.configure(api_key=next_key)
                                
                                # Tenta diferentes modelos disponíveis
                                models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                                model = None
                                
                                for model_name in models_to_try:
                                    try:
                                        model = genai.GenerativeModel(model_name)
                                        # Testa o modelo
                                        test_response = model.generate_content("OK")
                                        if test_response:
                                            break
                                    except Exception:
                                        continue
                                
                                if model:
                                    self.log_message(f"   🔄 Alternando para chave {self.current_api_index + 1} (modelo: {model_name})...", "INFO")
                                else:
                                    self.log_message(f"   ❌ Nenhum modelo disponível para chave {self.current_api_index + 1}", "ERROR")
                                    
                            except Exception as config_error:
                                self.log_message(f"   ❌ Erro ao configurar nova chave: {config_error}", "ERROR")
                    
                    self.log_message(f"   ⏱️ Aguardando 5 segundos...", "INFO")
                    time.sleep(5)
                else:
                    self.log_message(f"   🔄 Todas as chaves testadas, usando análise de fallback...", "WARNING")
                    return self.fallback_analysis(file_name)
                    
    def fallback_analysis(self, file_name):
        """Análise de fallback baseada no nome do arquivo"""
        file_name_lower = file_name.lower()
        
        # Detecta banco
        if 'caixa' in file_name_lower:
            banco = 'CAIXA'
        elif any(term in file_name_lower for term in ['bb', 'brasil', 'banco do brasil']):
            banco = 'BANCO_DO_BRASIL'
        else:
            banco = 'CAIXA'
            
        # Detecta tipo de conta
        if any(term in file_name_lower for term in ['invest', 'aplicacao', 'fundo']):
            tipo_conta = 'investimento'
        elif 'poupanca' in file_name_lower:
            tipo_conta = 'poupanca'
        else:
            tipo_conta = 'corrente'
            
        # Detecta mês e ano
        mes_patterns = {
            'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
            'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12,
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
            'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }
        
        mes = None
        for mes_nome, mes_num in mes_patterns.items():
            if mes_nome in file_name_lower:
                mes = mes_num
                break
                
        # Busca ano
        ano_match = re.search(r'20(\d{2})', file_name)
        ano = int(f"20{ano_match.group(1)}") if ano_match else datetime.now().year
        
        if mes is None:
            mes = datetime.now().month
            
        return {
            'banco': banco,
            'mes': mes,
            'ano': ano,
            'tipo_conta': tipo_conta
        }
        
    def create_organized_structure(self, analysis_result):
        """Cria a estrutura de pastas organizada"""
        output_base = os.path.join(self.base_directory.get(), self.output_directory.get())
        
        ano = str(analysis_result['ano'])
        mes = MES_NOMES[analysis_result['mes']]
        banco = analysis_result['banco']
        tipo_conta = analysis_result['tipo_conta'].upper()
        file_type = analysis_result.get('file_type', 'PDF')
        
        folder_path = os.path.join(output_base, ano, mes, banco, tipo_conta, file_type)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
        
    def copy_file_to_destination(self, source_path, destination_folder, original_name):
        """Copia arquivo para o destino mantendo o original seguro"""
        destination_path = os.path.join(destination_folder, original_name)
        
        # Validações de segurança
        if not os.path.exists(source_path):
            self.log_message(f"❌ Arquivo original não encontrado: {source_path}", "ERROR")
            return None
            
        if not os.access(source_path, os.R_OK):
            self.log_message(f"❌ Sem permissão de leitura: {source_path}", "ERROR")
            return None
        
        # Evita duplicatas com numeração
        counter = 1
        base_name, extension = os.path.splitext(original_name)
        while os.path.exists(destination_path):
            new_name = f"{base_name}_{counter}{extension}"
            destination_path = os.path.join(destination_folder, new_name)
            counter += 1
            
        try:
            # Verifica espaço em disco antes de copiar
            source_size = os.path.getsize(source_path)
            free_space = shutil.disk_usage(destination_folder).free
            
            if source_size > free_space:
                self.log_message(f"❌ Espaço insuficiente em disco para copiar {original_name}", "ERROR")
                return None
            
            # Copia preservando metadados (shutil.copy2 mantém timestamps)
            self.log_message(f"   📋 Copiando {original_name} (preservando original)...", "INFO")
            shutil.copy2(source_path, destination_path)
            
            # Verifica integridade da cópia
            if os.path.exists(destination_path):
                source_size = os.path.getsize(source_path)
                dest_size = os.path.getsize(destination_path)
                
                if source_size == dest_size:
                    self.log_message(f"   ✅ Cópia verificada: {os.path.basename(destination_path)}", "SUCCESS")
                    self.log_message(f"   🛡️ Original preservado em: {source_path}", "INFO")
                    return destination_path
                else:
                    # Remove cópia corrompida
                    os.remove(destination_path)
                    self.log_message(f"❌ Cópia corrompida removida - tamanhos diferentes", "ERROR")
                    return None
            else:
                self.log_message(f"❌ Falha na criação da cópia", "ERROR")
                return None
                
        except PermissionError as e:
            self.log_message(f"❌ Erro de permissão ao copiar: {e}", "ERROR")
            return None
        except OSError as e:
            self.log_message(f"❌ Erro do sistema ao copiar: {e}", "ERROR")
            return None
        except Exception as e:
            self.log_message(f"❌ Erro inesperado ao copiar arquivo: {e}", "ERROR")
            return None
            
    def show_final_stats(self):
        """Mostra estatísticas finais"""
        self.log_message("="*60, "INFO")
        self.log_message("📊 RESUMO FINAL", "INFO")
        self.log_message("="*60, "INFO")
        self.log_message(f"✅ Arquivos processados com sucesso: {self.stats['success']}", "SUCCESS")
        self.log_message(f"❌ Erros: {self.stats['errors']}", "ERROR" if self.stats['errors'] > 0 else "INFO")
        self.log_message(f"📁 Total de arquivos: {self.stats['total_files']}", "INFO")
        
        if self.stats['by_bank']:
            self.log_message("", "INFO")
            self.log_message("📈 Por banco:", "INFO")
            for banco, count in self.stats['by_bank'].items():
                self.log_message(f"   {banco}: {count} arquivos", "INFO")
                
        if self.stats['by_month']:
            self.log_message("", "INFO")
            self.log_message("📅 Por mês:", "INFO")
            for mes_ano, count in sorted(self.stats['by_month'].items()):
                self.log_message(f"   {mes_ano}: {count} arquivos", "INFO")
                
        if self.stats.get('by_account_type'):
            self.log_message("", "INFO")
            self.log_message("💳 Por tipo de conta:", "INFO")
            for tipo, count in self.stats['by_account_type'].items():
                emoji = "💰" if tipo == "corrente" else "🏦" if tipo == "poupanca" else "📈"
                self.log_message(f"   {emoji} {tipo.title()}: {count} arquivos", "INFO")
                
        if self.stats.get('by_format'):
            self.log_message("", "INFO")
            self.log_message("📄 Por formato:", "INFO")
            for formato, count in self.stats['by_format'].items():
                emoji = "📄" if formato == "PDF" else "💾"
                self.log_message(f"   {emoji} {formato}: {count} arquivos", "INFO")
                
        output_path = os.path.join(self.base_directory.get(), self.output_directory.get())
        self.log_message(f"\n📁 Arquivos organizados em: {output_path}", "SUCCESS")
        
        # Atualiza aba de resultados
        self.update_results_tab()
        
    def update_results_tab(self):
        """Atualiza a aba de resultados"""
        self.stats_text.config(state=NORMAL)
        self.stats_text.delete(1.0, END)
        
        stats_content = f"""📊 ESTATÍSTICAS DO PROCESSAMENTO

✅ Arquivos processados com sucesso: {self.stats['success']}
❌ Erros encontrados: {self.stats['errors']}
📁 Total de arquivos: {self.stats['total_files']}

📈 DISTRIBUIÇÃO POR BANCO:
"""
        
        for banco, count in self.stats['by_bank'].items():
            stats_content += f"   • {banco}: {count} arquivos\n"
            
        stats_content += "\n📅 DISTRIBUIÇÃO POR MÊS:\n"
        
        for mes_ano, count in sorted(self.stats['by_month'].items()):
            stats_content += f"   • {mes_ano}: {count} arquivos\n"
            
        if self.stats.get('by_account_type'):
            stats_content += "\n💳 DISTRIBUIÇÃO POR TIPO DE CONTA:\n"
            for tipo, count in self.stats['by_account_type'].items():
                emoji = "💰" if tipo == "corrente" else "🏦" if tipo == "poupanca" else "📈"
                stats_content += f"   {emoji} {tipo.title()}: {count} arquivos\n"
                
        if self.stats.get('by_format'):
            stats_content += "\n📄 DISTRIBUIÇÃO POR FORMATO:\n"
            for formato, count in self.stats['by_format'].items():
                emoji = "📄" if formato == "PDF" else "💾"
                stats_content += f"   {emoji} {formato}: {count} arquivos\n"
            
        output_path = os.path.join(self.base_directory.get(), self.output_directory.get())
        stats_content += f"\n📁 LOCALIZAÇÃO DOS ARQUIVOS ORGANIZADOS:\n{output_path}"
        
        self.stats_text.insert(1.0, stats_content)
        self.stats_text.config(state=DISABLED)
        
    def open_output_folder(self):
        """Abre a pasta de saída no explorador"""
        output_path = os.path.join(self.base_directory.get(), self.output_directory.get())
        if os.path.exists(output_path):
            os.startfile(output_path)
        else:
            messagebox.showwarning("Aviso", "Pasta organizada ainda não foi criada!")
            
    def save_log(self):
        """Salva o log em arquivo"""
        log_content = self.log_text.get(1.0, END)
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar Log",
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                messagebox.showinfo("Sucesso", f"Log salvo em:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar log:\n{str(e)}")
                
    def reset_processing(self):
        """Reseta o processamento para uma nova execução"""
        self.processing = False
        self.start_button.config(state=NORMAL)
        self.stop_button.config(state=DISABLED)
        
        # Limpa log
        self.log_text.config(state=NORMAL)
        self.log_text.delete(1.0, END)
        self.log_text.config(state=DISABLED)
        
        # Reseta progresso
        self.progress_var.set(0)
        self.progress_label.config(text="Aguardando início...")
        
        # Limpa estatísticas
        self.stats_text.config(state=NORMAL)
        self.stats_text.delete(1.0, END)
        self.stats_text.config(state=DISABLED)
        
        # Volta para primeira aba
        self.notebook.select(0)
        
        self.status_label.config(text="Pronto para novo processamento")
        
    def get_app_data_directory(self):
        """Cria e retorna diretório de dados do aplicativo"""
        if os.name == 'nt':  # Windows
            app_data = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'OrganizadorExtratos')
        else:  # Linux/Mac
            app_data = os.path.join(os.path.expanduser('~'), '.organizador_extratos')
        
        # Cria diretório se não existir
        os.makedirs(app_data, exist_ok=True)
        return app_data
        
    def save_api_keys(self):
        """Salva as chaves API em arquivo"""
        try:
            with open(self.api_keys_file, 'w', encoding='utf-8') as f:
                json.dump(self.api_keys, f, indent=2)
        except Exception as e:
            self.log_message(f"⚠️ Erro ao salvar chaves API: {e}", "WARNING")
            
    def load_api_keys(self):
        """Carrega as chaves API do arquivo"""
        try:
            if os.path.exists(self.api_keys_file):
                with open(self.api_keys_file, 'r', encoding='utf-8') as f:
                    self.api_keys = json.load(f)
        except Exception as e:
            self.api_keys = []
            
    def update_keys_display(self):
        """Atualiza a exibição da lista de chaves"""
        self.keys_listbox.delete(0, END)
        
        for i, key in enumerate(self.api_keys):
            # Mostra apenas os primeiros e últimos caracteres da chave
            masked_key = f"Chave {i + 1}: {key[:8]}...{key[-8:]}" if len(key) > 16 else f"Chave {i + 1}: {key}"
            self.keys_listbox.insert(END, masked_key)
            
        # Atualiza status
        if self.api_keys:
            self.api_status_label.config(text=f"{len(self.api_keys)} chave(s) configurada(s)")
        else:
            self.api_status_label.config(text="Nenhuma chave configurada")
        
    def save_checkpoint(self, files, current_index, stats):
        """Salva o checkpoint do processamento"""
        try:
            checkpoint_data = {
                'timestamp': datetime.now().isoformat(),
                'base_directory': self.base_directory.get(),
                'output_directory': self.output_directory.get(),
                'current_index': current_index,
                'total_files': len(files),
                'files': [str(f) for f in files],
                'stats': stats,
                'api_keys_count': len(self.api_keys),
                 'current_api_index': self.current_api_index
            }
            
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.log_message(f"⚠️ Erro ao salvar checkpoint: {e}", "WARNING")
            
    def load_checkpoint(self):
        """Carrega o checkpoint do processamento"""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.log_message(f"⚠️ Erro ao carregar checkpoint: {e}", "WARNING")
        return None
        
    def has_checkpoint(self):
        """Verifica se existe um checkpoint válido"""
        checkpoint_data = self.load_checkpoint()
        return checkpoint_data is not None and checkpoint_data.get('current_index', 0) > 0
        
    def clear_checkpoint(self):
        """Remove o arquivo de checkpoint"""
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
                self.resume_button.config(state=DISABLED)
                self.log_message("🗑️ Checkpoint removido", "INFO")
                messagebox.showinfo("Checkpoint", "Checkpoint removido com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover checkpoint: {e}")
            
    def check_for_checkpoint(self):
        """Verifica se há checkpoint ao iniciar o programa"""
        if self.has_checkpoint():
            checkpoint_data = self.load_checkpoint()
            if checkpoint_data:
                current_index = checkpoint_data.get('current_index', 0)
                total_files = checkpoint_data.get('total_files', 0)
                timestamp = checkpoint_data.get('timestamp', 'Desconhecido')
                
                self.resume_button.config(state=NORMAL)
                self.status_label.config(text=f"Checkpoint encontrado: arquivo {current_index + 1}/{total_files}")
                
                # Mostra notificação
                response = messagebox.askyesno(
                    "Checkpoint Encontrado", 
                    f"Encontrado processamento interrompido:\n\n"
                    f"📅 Data: {timestamp[:19].replace('T', ' ')}\n"
                    f"📄 Parou no arquivo: {current_index + 1}/{total_files}\n"
                    f"📊 Progresso: {(current_index/total_files)*100:.1f}%\n\n"
                    f"Deseja retomar automaticamente?"
                )
                
                if response:
                    # Agenda retomada automática após 2 segundos
                    self.root.after(2000, self.resume_processing)
                    
    def resume_processing(self):
        """Retoma o processamento do checkpoint"""
        if self.processing:
            return
            
        checkpoint_data = self.load_checkpoint()
        if not checkpoint_data:
            messagebox.showerror("Erro", "Nenhum checkpoint válido encontrado!")
            return
            
        # Validações
        if not self.api_keys:
            messagebox.showerror("Erro", "Configure pelo menos uma chave da API primeiro!")
            self.notebook.select(0)
            return
            
        # Restaura configurações do checkpoint
        self.base_directory.set(checkpoint_data.get('base_directory', os.getcwd()))
        self.output_directory.set(checkpoint_data.get('output_directory', 'EXTRATOS_ORGANIZADOS'))
        
        files = [Path(f) for f in checkpoint_data.get('files', [])]
        start_index = checkpoint_data.get('current_index', 0)
        
        if start_index >= len(files):
            messagebox.showinfo("Concluído", "Todos os arquivos já foram processados!")
            self.clear_checkpoint()
            return
            
        # Configura interface para processamento
        self.processing = True
        self.start_button.config(state=DISABLED)
        self.resume_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        self.notebook.select(1)
        
        # Inicia thread de processamento do checkpoint
        self.processing_thread = threading.Thread(target=self.process_files, args=(files, start_index))
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
# ==================== EXECUÇÃO PRINCIPAL ====================

def main():
    """Função principal"""
    root = Tk()
    app = OrganizadorExtratosGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Programa encerrado pelo usuário")
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Erro inesperado:\n{str(e)}")
        
if __name__ == "__main__":
    main()