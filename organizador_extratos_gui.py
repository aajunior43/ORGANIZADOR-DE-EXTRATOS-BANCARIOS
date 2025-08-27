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
        self.load_preferences()  # Carrega depois da UI ser criada
        self.apply_theme()
        self.check_dependencies()
        self.load_api_keys()
        self.check_for_checkpoint()
        
    def setup_window(self):
        """Configura a janela principal"""
        self.root.title("🏦 Organizador de Extratos Bancários - Gemini AI")
        self.root.geometry("1100x800")
        self.root.minsize(900, 700)
        
        # Centraliza a janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1100 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1100x800+{x}+{y}")
        
        # Configura o estilo moderno
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configura cores personalizadas para o tema
        self.configure_modern_style()
        
    def configure_modern_style(self):
        """Configura estilo moderno e profissional para os componentes"""
        # Cores modernas inspiradas no VS Code e Microsoft Fluent Design
        colors = {
            'primary': '#0078d4',      # Azul Microsoft
            'primary_dark': '#106ebe', # Azul escuro
            'success': '#107c10',      # Verde Microsoft
            'warning': '#ff8c00',      # Laranja Microsoft
            'error': '#d13438',        # Vermelho Microsoft
            'surface': '#ffffff',      # Branco puro
            'surface_alt': '#f3f2f1',  # Cinza claro Microsoft
            'text': '#323130',         # Texto escuro Microsoft
            'text_secondary': '#605e5c', # Texto secundário
            'border': '#edebe9',       # Borda sutil
            'hover': '#f3f2f1'         # Estado hover
        }
        
        # Estilo para Notebook (abas) - Design moderno
        self.style.configure('Modern.TNotebook', 
                           background=colors['surface'],
                           borderwidth=0,
                           tabmargins=[0, 0, 0, 0])
        
        self.style.configure('Modern.TNotebook.Tab', 
                           padding=[24, 16, 24, 16],
                           font=('Segoe UI', 11, 'normal'),
                           background=colors['surface_alt'],
                           foreground=colors['text'],
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map('Modern.TNotebook.Tab',
                      background=[('selected', colors['surface']),
                                ('active', colors['hover']),
                                ('!active', colors['surface_alt'])],
                      foreground=[('selected', colors['primary']),
                                ('active', colors['text']),
                                ('!active', colors['text_secondary'])],
                      expand=[('selected', [1, 1, 1, 0])])
        
        # Estilo para Progressbar - Design fluent
        self.style.configure('Modern.Horizontal.TProgressbar',
                           background=colors['primary'],
                           troughcolor=colors['surface_alt'],
                           borderwidth=0,
                           lightcolor=colors['primary'],
                           darkcolor=colors['primary'],
                           troughrelief='flat',
                           relief='flat')
        
        # Estilo para LabelFrame - Cards modernos
        self.style.configure('Modern.TLabelframe',
                           background=colors['surface'],
                           borderwidth=1,
                           relief='solid',
                           bordercolor=colors['border'])
        
        self.style.configure('Modern.TLabelframe.Label',
                           background=colors['surface'],
                           foreground=colors['text'],
                           font=('Segoe UI', 12, 'bold'))
        
        # Estilo para Buttons - Fluent Design
        self.style.configure('Modern.TButton',
                           background=colors['primary'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'normal'),
                           padding=[16, 8])
        
        self.style.map('Modern.TButton',
                      background=[('active', colors['primary_dark']),
                                ('pressed', colors['primary_dark'])])
        
        # Botão secundário
        self.style.configure('Secondary.TButton',
                           background=colors['surface_alt'],
                           foreground=colors['text'],
                           borderwidth=1,
                           bordercolor=colors['border'],
                           focuscolor='none',
                           font=('Segoe UI', 10, 'normal'),
                           padding=[16, 8])
        
        self.style.map('Secondary.TButton',
                      background=[('active', colors['hover']),
                                ('pressed', colors['hover'])])
        
        # Botão de sucesso
        self.style.configure('Success.TButton',
                           background=colors['success'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'bold'),
                           padding=[16, 8])
        
        # Botão de perigo
        self.style.configure('Danger.TButton',
                           background=colors['error'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10, 'normal'),
                           padding=[16, 8])
        
        # Entry moderno
        self.style.configure('Modern.TEntry',
                           fieldbackground=colors['surface'],
                           borderwidth=1,
                           bordercolor=colors['border'],
                           focuscolor=colors['primary'],
                           font=('Segoe UI', 10))
        
        # Combobox moderno
        self.style.configure('Modern.TCombobox',
                           fieldbackground=colors['surface'],
                           borderwidth=1,
                           bordercolor=colors['border'],
                           focuscolor=colors['primary'],
                           font=('Segoe UI', 10))
        
        # Scrollbar moderna
        self.style.configure('Modern.Vertical.TScrollbar',
                           background=colors['surface_alt'],
                           troughcolor=colors['surface_alt'],
                           borderwidth=0,
                           arrowcolor=colors['text_secondary'],
                           darkcolor=colors['surface_alt'],
                           lightcolor=colors['surface_alt'])
        
        # Armazena as cores para uso posterior
        self.modern_colors = colors
        
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
        
        # Configuração de intervalo entre arquivos (em segundos)
        self.processing_interval = 10  # Padrão: 10 segundos (balanceado)
        self.interval_var = None  # Será inicializado na interface
        
        # Arquivos de configuração no diretório de dados do app
        self.checkpoint_file = os.path.join(self.app_data_dir, "processing_checkpoint.json")
        self.api_keys_file = os.path.join(self.app_data_dir, "api_keys.json")
        self.preferences_file = os.path.join(self.app_data_dir, "preferences.json")
        
        # Sistema de temas
        self.current_theme = "light"  # light ou dark
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "select_bg": "#0078d4",
                "select_fg": "#ffffff",
                "entry_bg": "#ffffff",
                "entry_fg": "#000000",
                "button_bg": "#f0f0f0",
                "button_fg": "#000000",
                "frame_bg": "#f8f9fa",
                "text_bg": "#ffffff",
                "text_fg": "#000000",
                "success_fg": "#28a745",
                "error_fg": "#dc3545",
                "warning_fg": "#ffc107"
            },
            "dark": {
                "bg": "#1e1e1e",              # Fundo principal escuro moderno
                "fg": "#ffffff",              # Texto principal branco
                "select_bg": "#0078d4",        # Azul Microsoft para seleções
                "select_fg": "#ffffff",        # Texto em seleções branco
                "entry_bg": "#2d2d30",         # Campos de entrada VS Code style
                "entry_fg": "#ffffff",         # Texto em campos branco
                "button_bg": "#0e639c",        # Botões azul Microsoft
                "button_fg": "#ffffff",        # Texto de botões branco
                "frame_bg": "#252526",         # Frames VS Code style
                "text_bg": "#1e1e1e",          # Áreas de texto escuras
                "text_fg": "#d4d4d4",          # Texto em áreas VS Code style
                "success_fg": "#4ec9b0",       # Verde VS Code
                "error_fg": "#f48771",         # Vermelho VS Code
                "warning_fg": "#dcdcaa",       # Amarelo VS Code
                "accent": "#007acc",           # Azul VS Code como destaque
                "secondary": "#3c3c3c",        # Cinza VS Code para elementos secundários
                "border": "#3e3e42",           # Bordas VS Code
                "hover": "#2a2d2e",            # Estado hover VS Code
                "primary": "#007acc",          # Cor primária
                "background": "#1e1e1e"       # Fundo geral
            }
        }
        
        self.stats = {
            'total_files': 0,
            'success': 0,
            'errors': 0,
            'by_bank': {},
            'by_month': {}
        }
        
        # Inicializa cores baseadas no tema atual
        self.update_colors()
        
    def update_colors(self):
        """Atualiza as cores baseadas no tema atual"""
        theme = self.themes[self.current_theme]
        self.colors = {
            'background': theme.get('bg', '#ffffff'),
            'text': theme.get('fg', '#000000'),
            'primary': theme.get('accent', '#007bff'),
            'secondary': theme.get('secondary', '#6c757d'),
            'success': theme.get('success_fg', '#28a745'),
            'error': theme.get('error_fg', '#dc3545'),
            'warning': theme.get('warning_fg', '#ffc107'),
            'frame_bg': theme.get('frame_bg', '#f8f9fa'),
            'entry_bg': theme.get('entry_bg', '#ffffff'),
            'entry_fg': theme.get('entry_fg', '#000000'),
            'button_bg': theme.get('button_bg', '#007bff'),
            'button_fg': theme.get('button_fg', '#ffffff')
        }
        
        # Carrega chaves salvas
        self.load_api_keys()
        
    def setup_ui(self):
        """Configura a interface do usuário moderna"""
        # Frame principal com gradiente visual
        main_frame = Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=BOTH, expand=True, padx=15, pady=15)
        
        # Cabeçalho moderno com design aprimorado
        self.setup_modern_header(main_frame)
        
        # Notebook para abas com estilo moderno
        self.notebook = ttk.Notebook(main_frame, style='TNotebook')
        self.notebook.pack(fill=BOTH, expand=True, pady=(20, 0))
        
        # Aba 1: Configuração
        self.setup_config_tab()
        
        # Aba 2: Processamento
        self.setup_processing_tab()
        
        # Aba 3: Resultados
        self.setup_results_tab()
        
        # Frame de status moderno na parte inferior
        self.setup_modern_status_frame(main_frame)
        
        # Verifica se há checkpoint para retomar (após criar todos os componentes)
        self.check_for_checkpoint()
    
    def create_modern_section(self, parent, title, description="", icon=""):
        """Cria uma seção moderna estilo card com sombra e design fluent"""
        # Container com padding para simular sombra
        shadow_frame = Frame(parent, bg='#e5e5e5', height=2)
        shadow_frame.pack(fill=X, padx=(2, 0), pady=(0, 2))
        
        # Frame principal da seção - Card moderno
        section_frame = Frame(parent, 
                             bg=self.modern_colors['surface'], 
                             relief='flat', 
                             bd=0,
                             highlightbackground=self.modern_colors['border'],
                             highlightthickness=1)
        
        # Cabeçalho da seção com gradiente visual
        header_frame = Frame(section_frame, 
                            bg=self.modern_colors['surface'],
                            height=60)
        header_frame.pack(fill=X)
        header_frame.pack_propagate(False)
        
        # Container do título com ícone
        title_container = Frame(header_frame, bg=self.modern_colors['surface'])
        title_container.pack(fill=BOTH, expand=True, padx=20, pady=16)
        
        # Linha do título com ícone
        title_line = Frame(title_container, bg=self.modern_colors['surface'])
        title_line.pack(fill=X)
        
        # Ícone (se fornecido)
        if icon:
            icon_label = Label(title_line, 
                              text=icon, 
                              font=("Segoe UI Emoji", 16),
                              bg=self.modern_colors['surface'],
                              fg=self.modern_colors['primary'])
            icon_label.pack(side=LEFT, padx=(0, 12))
        
        # Título principal
        title_label = Label(title_line, 
                           text=title, 
                           font=("Segoe UI", 14, "bold"),
                           bg=self.modern_colors['surface'],
                           fg=self.modern_colors['text'])
        title_label.pack(side=LEFT, anchor=W)
        
        # Descrição (se fornecida)
        if description:
            desc_label = Label(title_container, 
                              text=description,
                              font=("Segoe UI", 10),
                              bg=self.modern_colors['surface'],
                              fg=self.modern_colors['text_secondary'],
                              wraplength=600,
                              justify=LEFT)
            desc_label.pack(anchor=W, pady=(8, 0))
        
        # Linha separadora sutil
        separator = Frame(section_frame, 
                         bg=self.modern_colors['border'], 
                         height=1)
        separator.pack(fill=X, padx=20)
        
        # Área de conteúdo com padding interno
        content_frame = Frame(section_frame, 
                             bg=self.modern_colors['surface'],
                             padx=20, 
                             pady=20)
        content_frame.pack(fill=BOTH, expand=True)
        
        return content_frame
        
    def setup_modern_header(self, parent):
        """Configura cabeçalho moderno"""
        # Container do cabeçalho com fundo gradiente simulado
        header_container = Frame(parent, bg=self.colors['background'], height=80)
        header_container.pack(fill=X, pady=(0, 20))
        header_container.pack_propagate(False)
        
        # Frame principal do cabeçalho
        header_frame = Frame(header_container, bg='#ffffff' if self.current_theme == 'light' else '#252526', 
                           relief='flat', bd=0)
        header_frame.pack(fill=BOTH, expand=True, padx=2, pady=2)
        
        # Linha superior com título e controles
        top_line = Frame(header_frame, bg='#ffffff' if self.current_theme == 'light' else '#252526')
        top_line.pack(fill=X, padx=20, pady=(15, 5))
        
        # Área do título
        title_area = Frame(top_line, bg='#ffffff' if self.current_theme == 'light' else '#252526')
        title_area.pack(side=LEFT, fill=X, expand=True)
        
        # Título principal com fonte moderna
        title_font = Font(family="Segoe UI", size=22, weight="bold")
        title_label = Label(title_area, text="🏦 Organizador de Extratos Bancários", 
                           font=title_font, 
                           bg='#ffffff' if self.current_theme == 'light' else '#252526',
                           fg=self.colors['primary'])
        title_label.pack(anchor=W)
        
        # Subtítulo com estilo moderno
        subtitle_font = Font(family="Segoe UI", size=11)
        subtitle_label = Label(title_area, text="Powered by Google Gemini AI • Versão 2.0", 
                              font=subtitle_font, 
                              bg='#ffffff' if self.current_theme == 'light' else '#252526',
                              fg='#6c757d' if self.current_theme == 'light' else '#9cdcfe')
        subtitle_label.pack(anchor=W, pady=(2, 0))
        
        # Área de controles
        controls_area = Frame(top_line, bg='#ffffff' if self.current_theme == 'light' else '#252526')
        controls_area.pack(side=RIGHT)
        
        # Botão de tema moderno
        theme_icon = "🌙" if self.current_theme == "light" else "☀️"
        theme_text = "Escuro" if self.current_theme == "light" else "Claro"
        
        self.theme_button = Button(controls_area, 
                                  text=f"{theme_icon} {theme_text}", 
                                  command=self.toggle_theme,
                                  font=Font(family="Segoe UI", size=10),
                                  bg=self.colors['secondary'],
                                  fg='white',
                                  relief='flat',
                                  padx=15, pady=8,
                                  cursor='hand2')
        self.theme_button.pack(side=RIGHT)
        
        # Linha inferior com informações de status
        bottom_line = Frame(header_frame, bg='#ffffff' if self.current_theme == 'light' else '#252526')
        bottom_line.pack(fill=X, padx=20, pady=(0, 15))
        
        # Indicadores de status
        status_area = Frame(bottom_line, bg='#ffffff' if self.current_theme == 'light' else '#252526')
        status_area.pack(side=LEFT)
        
        # Status das dependências
        self.header_deps_label = Label(status_area, text="Verificando dependências...", 
                                      font=Font(family="Segoe UI", size=9),
                                      bg='#ffffff' if self.current_theme == 'light' else '#252526',
                                      fg='#6c757d' if self.current_theme == 'light' else '#9cdcfe')
        self.header_deps_label.pack(side=LEFT, padx=(0, 20))
        
        # Status das chaves API
        self.header_api_label = Label(status_area, text="Nenhuma chave configurada", 
                                     font=Font(family="Segoe UI", size=9),
                                     bg='#ffffff' if self.current_theme == 'light' else '#252526',
                                     fg='#6c757d' if self.current_theme == 'light' else '#9cdcfe')
        self.header_api_label.pack(side=LEFT)
        
    def setup_config_tab(self):
        """Configura a aba de configuração com design moderno"""
        # Container principal com scroll
        config_container = Frame(self.notebook, bg='#ffffff' if self.current_theme == 'light' else '#1e1e1e')
        self.notebook.add(config_container, text="⚙️ Configuração")
        
        # Canvas para scroll
        canvas = Canvas(config_container, bg='#ffffff' if self.current_theme == 'light' else '#1e1e1e',
                       highlightthickness=0)
        scrollbar = Scrollbar(config_container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg='#ffffff' if self.current_theme == 'light' else '#1e1e1e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        config_frame = scrollable_frame
        
        # Seção API Keys com design moderno
        api_section = self.create_modern_section(config_frame, "🔑 Chaves da API do Gemini", 
                                                "Configure suas chaves do Google Gemini para análise de IA")
        api_section.pack(fill=X, padx=25, pady=(20, 15))
        
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
        
        # Seção Configurações de Processamento
        processing_section = LabelFrame(config_frame, text="⚙️ Configurações de Processamento", 
                                       font=("Arial", 12, "bold"), bg='#f8f9fa', fg='#000000')
        processing_section.pack(fill=X, padx=20, pady=10)
        
        # Aviso sobre rate limiting
        rate_limit_frame = Frame(processing_section, bg='#fff3cd', relief=RIDGE, bd=1)
        rate_limit_frame.pack(fill=X, padx=10, pady=(10, 5))
        
        Label(rate_limit_frame, text="⚠️ CONTROLE DE RATE LIMIT", 
              bg='#fff3cd', fg='#856404', font=("Arial", 10, "bold")).pack(pady=2)
        Label(rate_limit_frame, text="• Configure o intervalo entre requests para evitar bloqueios da API", 
              bg='#fff3cd', fg='#856404', font=("Arial", 9)).pack(anchor=W, padx=5)
        Label(rate_limit_frame, text="• Intervalos menores = processamento mais rápido, mas risco de rate limit", 
              bg='#fff3cd', fg='#856404', font=("Arial", 9)).pack(anchor=W, padx=5, pady=(0, 2))
        
        # Intervalo entre arquivos
        interval_frame = Frame(processing_section, bg='#f8f9fa')
        interval_frame.pack(fill=X, padx=10, pady=10)
        
        Label(interval_frame, text="⏱️ Intervalo entre requests da API (segundos):", 
              bg='#f8f9fa', font=("Arial", 11, "bold"), fg='#000000').pack(side=LEFT)
        
        # Spinbox para selecionar intervalo
        self.interval_var = IntVar(value=self.processing_interval)
        interval_spinbox = Spinbox(interval_frame, from_=1, to=60, width=8, 
                                  textvariable=self.interval_var, font=("Arial", 12, "bold"),
                                  command=self.update_interval, bg='white', fg='#000000',
                                  relief='solid', bd=2)
        interval_spinbox.pack(side=LEFT, padx=(10, 5))
        
        Label(interval_frame, text="(1-60 segundos)", 
              bg='#f8f9fa', font=("Arial", 10), 
              fg='#666666').pack(side=LEFT)
        
        # Botão para aplicar intervalo
        apply_interval_btn = Button(interval_frame, text="✅ Aplicar", 
                                   command=self.update_interval,
                                   bg='#28a745', fg='white', font=("Arial", 9))
        apply_interval_btn.pack(side=LEFT, padx=(10, 0))
        
        # Descrições dos intervalos
        descriptions_frame = Frame(processing_section, bg='#f8f9fa')
        descriptions_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        Label(descriptions_frame, 
              text="💡 Recomendações:", 
              bg='#f8f9fa', font=("Arial", 10, "bold"), 
              fg='#000000').pack(anchor=W)
        
        Label(descriptions_frame, 
              text="   • 1-5 segundos: Rápido, mas pode causar rate limit", 
              bg='#f8f9fa', font=("Arial", 9), 
              fg='#dc3545').pack(anchor=W, padx=10)
              
        Label(descriptions_frame, 
              text="   • 6-10 segundos: Balanceado (recomendado)", 
              bg='#f8f9fa', font=("Arial", 9), 
              fg='#28a745').pack(anchor=W, padx=10)
              
        Label(descriptions_frame, 
              text="   • 11+ segundos: Muito seguro, mas mais lento", 
              bg='#f8f9fa', font=("Arial", 9), 
              fg='#007bff').pack(anchor=W, padx=10)
        
        # Status do intervalo atual
        self.interval_status_label = Label(descriptions_frame, 
                                          text=f"🔧 Intervalo atual: {self.processing_interval} segundos", 
                                          bg='#f8f9fa', font=("Arial", 10, "bold"), 
                                          fg='#007bff')
        self.interval_status_label.pack(anchor=W, pady=(5, 0))
        
        # Controles rápidos de intervalo
        quick_controls_frame = Frame(processing_section, bg='#f8f9fa')
        quick_controls_frame.pack(fill=X, padx=10, pady=(5, 10))
        
        Label(quick_controls_frame, text="🚀 Configurações Rápidas:", 
              bg='#f8f9fa', font=("Arial", 10, "bold"), fg='#000000').pack(anchor=W)
        
        buttons_frame = Frame(quick_controls_frame, bg='#f8f9fa')
        buttons_frame.pack(fill=X, pady=5)
        
        # Botões de configuração rápida
        Button(buttons_frame, text="⚡ Rápido (5s)", 
               command=lambda: self.set_quick_interval(5),
               bg='#dc3545', fg='white', font=("Arial", 9), width=12).pack(side=LEFT, padx=(0, 5))
        
        Button(buttons_frame, text="⚖️ Balanceado (8s)", 
               command=lambda: self.set_quick_interval(8),
               bg='#28a745', fg='white', font=("Arial", 9), width=15).pack(side=LEFT, padx=(0, 5))
        
        Button(buttons_frame, text="🛡️ Seguro (15s)", 
               command=lambda: self.set_quick_interval(15),
               bg='#007bff', fg='white', font=("Arial", 9), width=12).pack(side=LEFT, padx=(0, 5))
        
        Button(buttons_frame, text="🐌 Ultra Seguro (30s)", 
               command=lambda: self.set_quick_interval(30),
               bg='#6f42c1', fg='white', font=("Arial", 9), width=16).pack(side=LEFT, padx=(0, 5))
        
        # Estimativa de tempo
        self.time_estimate_label = Label(quick_controls_frame, 
                                        text="📊 Estimativa: Configure o intervalo para ver o tempo estimado", 
                                        bg='#f8f9fa', font=("Arial", 9), fg='#666666')
        self.time_estimate_label.pack(anchor=W, pady=(5, 0))
        
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
               bg=self.colors['secondary'], fg='white', font=("Arial", 10)).pack(side=LEFT, padx=(0, 10))
        
        Button(actions_buttons, text="👁️ Ver Checkpoint",
               command=self.view_checkpoint,
               bg=self.colors['primary'], fg='white', font=("Arial", 10)).pack(side=LEFT)
        
    def setup_modern_status_frame(self, parent):
        """Configura a barra de status moderna"""
        status_container = Frame(parent, bg=self.colors['background'], height=40)
        status_container.pack(fill=X, side=BOTTOM, pady=(15, 0))
        status_container.pack_propagate(False)
        
        # Frame da barra de status com bordas arredondadas simuladas
        status_frame = Frame(status_container, 
                           bg='#f8f9fa' if self.current_theme == 'light' else '#2d2d30',
                           relief='flat', bd=0)
        status_frame.pack(fill=BOTH, expand=True, padx=2, pady=2)
        
        # Status principal
        self.status_label = Label(status_frame, text="🚀 Pronto para começar", 
                                 bg='#f8f9fa' if self.current_theme == 'light' else '#2d2d30',
                                 fg='#495057' if self.current_theme == 'light' else '#d4d4d4',
                                 font=Font(family="Segoe UI", size=10))
        self.status_label.pack(side=LEFT, padx=15, pady=10)
        
        # Área de indicadores à direita
        indicators_frame = Frame(status_frame, 
                               bg='#f8f9fa' if self.current_theme == 'light' else '#2d2d30')
        indicators_frame.pack(side=RIGHT, padx=15, pady=5)
        
        # Indicador de dependências
        self.deps_label = Label(indicators_frame, text="Verificando dependências...", 
                               bg='#f8f9fa' if self.current_theme == 'light' else '#2d2d30',
                               fg='#6c757d' if self.current_theme == 'light' else '#9cdcfe',
                               font=Font(family="Segoe UI", size=9))
        self.deps_label.pack(side=RIGHT, padx=(20, 0))
        
        # Separador visual
        separator = Label(indicators_frame, text="•", 
                         bg='#f8f9fa' if self.current_theme == 'light' else '#2d2d30',
                         fg='#dee2e6' if self.current_theme == 'light' else '#3e3e42',
                         font=Font(family="Segoe UI", size=9))
        separator.pack(side=RIGHT, padx=10)
        
        # Indicador de tempo
        self.time_label = Label(indicators_frame, 
                               text=datetime.now().strftime("%H:%M"),
                               bg='#f8f9fa' if self.current_theme == 'light' else '#2d2d30',
                               fg='#6c757d' if self.current_theme == 'light' else '#9cdcfe',
                               font=Font(family="Segoe UI", size=9))
        self.time_label.pack(side=RIGHT)
        
        # Atualiza o relógio a cada minuto
        self.update_clock()
        
    def update_clock(self):
        """Atualiza o relógio na barra de status"""
        if hasattr(self, 'time_label'):
            current_time = datetime.now().strftime("%H:%M")
            self.time_label.config(text=current_time)
        # Agenda próxima atualização em 60 segundos
        self.root.after(60000, self.update_clock)
        
    def toggle_theme_and_update(self):
        """Alterna tema e atualiza interface"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.update_colors()
        self.apply_theme()
        self.save_preferences()
        
    def apply_theme(self):
        """Aplica o tema atual a todos os componentes"""
        if not hasattr(self, 'notebook'):
            return
            
        # Atualiza cores do tema
        theme = self.themes[self.current_theme]
        
        # Atualiza o botão de tema
        if hasattr(self, 'theme_button'):
            theme_icon = "🌙" if self.current_theme == "light" else "☀️"
            theme_text = "Escuro" if self.current_theme == "light" else "Claro"
            self.theme_button.config(text=f"{theme_icon} {theme_text}",
                                   bg=self.colors['secondary'])
        
        # Atualiza componentes principais
        self.root.configure(bg=theme.get('bg', '#ffffff'))
        
        # Reconfigura estilo moderno
        self.configure_modern_style()
        
        # Força atualização visual
        self.root.update_idletasks()
        
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
        
        # Usa cores do tema atual
        theme = self.themes[self.current_theme]
        
        # Cores por nível com base no tema
        if self.current_theme == "dark":
            colors = {
                "INFO": theme['text_fg'],
                "SUCCESS": theme['success_fg'], 
                "WARNING": theme['warning_fg'],
                "ERROR": theme['error_fg']
            }
        else:
            colors = {
                "INFO": "#333333",
                "SUCCESS": "#2e7d32", 
                "WARNING": "#f57c00",
                "ERROR": "#c62828"
            }
        
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, f"[{timestamp}] {message}\n")
        
        # Aplica cor à última linha
        line_start = self.log_text.index("end-2c linestart")
        line_end = self.log_text.index("end-2c lineend")
        
        tag_name = f"level_{level}_{timestamp}"
        self.log_text.tag_add(tag_name, line_start, line_end)
        self.log_text.tag_config(tag_name, foreground=colors.get(level, theme['text_fg']))
        
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
                
                # Pausa configurável entre arquivos
                if i < len(files) - 1 and self.processing:
                    self.log_message(f"⏱️ Aguardando {self.processing_interval} segundos antes do próximo arquivo...", "INFO")
                    for second in range(self.processing_interval):
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
        
        # Para investimento, não cria subpasta OFX pois todos OFX são de conta corrente
        if tipo_conta == 'INVESTIMENTO' and file_type == 'OFX':
            folder_path = os.path.join(output_base, ano, mes, banco, 'CORRENTE', file_type)
        else:
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
        """Atualiza a exibição das chaves na listbox"""
        self.keys_listbox.delete(0, END)
        
        for i, key in enumerate(self.api_keys):
            # Mostra apenas os primeiros e últimos caracteres da chave
            masked_key = f"Chave {i+1}: {key[:8]}...{key[-8:]}"
            self.keys_listbox.insert(END, masked_key)
            
        # Atualiza status
        if self.api_keys:
            self.api_status_label.config(text=f"{len(self.api_keys)} chave(s) configurada(s)")
        else:
            self.api_status_label.config(text="Nenhuma chave configurada")
            
    def set_quick_interval(self, seconds):
        """Define um intervalo rápido usando os botões predefinidos"""
        try:
            old_interval = self.processing_interval
            self.processing_interval = seconds
            
            # Atualiza o spinbox
            if hasattr(self, 'interval_var') and self.interval_var is not None:
                self.interval_var.set(seconds)
            
            # Salva as preferências
            self.save_preferences()
            
            # Atualiza os controles visuais
            self.update_interval_controls()
            
            # Determina o status de risco
            if seconds <= 5:
                risk = "ARRISCADO"
                risk_color = "🔴"
            elif seconds <= 10:
                risk = "RECOMENDADO"
                risk_color = "🟢"
            else:
                risk = "MUITO SEGURO"
                risk_color = "🔵"
            
            # Log da mudança
            if hasattr(self, 'log_message'):
                self.log_message(f"⚙️ Configuração rápida: {old_interval}s → {seconds}s ({risk})", "INFO")
            
            # Atualiza estimativa de tempo
            self.update_time_estimate()
            
            # Mensagem de confirmação mais discreta
            self.status_label.config(text=f"{risk_color} Intervalo: {seconds}s ({risk})")
            
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao definir intervalo: {e}")
    
    def update_interval(self):
        """Atualiza o intervalo de processamento e salva nas preferências"""
        try:
            new_interval = self.interval_var.get()
            if 1 <= new_interval <= 60:
                old_interval = self.processing_interval
                self.processing_interval = new_interval
                self.save_preferences()
                
                # Atualiza os controles visuais
                self.update_interval_controls()
                
                # Determina o status de risco
                if new_interval <= 5:
                    risk = "ARRISCADO"
                elif new_interval <= 10:
                    risk = "RECOMENDADO"
                else:
                    risk = "MUITO SEGURO"
                
                # Log da mudança
                if hasattr(self, 'log_message'):
                    self.log_message(f"⚙️ Intervalo atualizado: {old_interval}s → {new_interval}s ({risk})", "INFO")
                
                # Atualiza estimativa de tempo
                self.update_time_estimate()
                
                # Mensagem de confirmação
                messagebox.showinfo("Intervalo Atualizado", 
                                   f"✅ Intervalo configurado para {new_interval} segundos\n"
                                   f"📊 Status: {risk}\n\n"
                                   f"Esta configuração será aplicada no próximo processamento.")
                
            else:
                # Reverte para valor válido
                self.interval_var.set(self.processing_interval)
                messagebox.showwarning("Valor Inválido", 
                                      f"⚠️ O intervalo deve estar entre 1 e 60 segundos.\n"
                                      f"Valor atual mantido: {self.processing_interval} segundos")
        except Exception as e:
            self.interval_var.set(self.processing_interval)
            messagebox.showerror("Erro", f"❌ Erro ao atualizar intervalo: {e}\n"
                                        f"Valor revertido para: {self.processing_interval} segundos")
            
    def load_preferences(self):
        """Carrega preferências do usuário"""
        # Define valores padrão primeiro
        self.current_theme = 'light'
        self.processing_interval = 10
        
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                    self.current_theme = preferences.get('theme', 'light')
                    self.processing_interval = preferences.get('processing_interval', 10)
                    
        except Exception as e:
            print(f"Aviso: Usando configurações padrão - {e}")
        
        # Atualiza controles da interface se já existirem
        self.update_interval_controls()
    
    def update_interval_controls(self):
        """Atualiza os controles de intervalo na interface"""
        try:
            # Atualiza o spinbox se já foi criado
            if hasattr(self, 'interval_var') and self.interval_var is not None:
                self.interval_var.set(self.processing_interval)
            
            # Atualiza o status se já foi criado
            if hasattr(self, 'interval_status_label'):
                # Determina a cor baseada no intervalo
                if self.processing_interval <= 5:
                    color = '#dc3545'  # Vermelho - arriscado
                    risk = "ARRISCADO"
                elif self.processing_interval <= 10:
                    color = '#28a745'  # Verde - recomendado
                    risk = "RECOMENDADO"
                else:
                    color = '#007bff'  # Azul - seguro
                    risk = "MUITO SEGURO"
                
                self.interval_status_label.config(
                    text=f"🔧 Intervalo atual: {self.processing_interval} segundos ({risk})",
                    fg=color
                )
        except Exception as e:
            print(f"Aviso: Erro ao atualizar controles de intervalo - {e}")
            
    def save_preferences(self):
        """Salva preferências do usuário"""
        try:
            preferences = {
                'theme': self.current_theme,
                'processing_interval': self.processing_interval
            }
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar preferências: {e}")
            
    def toggle_theme(self):
        """Alterna entre tema claro e escuro"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme()
        self.save_preferences()
        
        # Atualiza o ícone do botão
        theme_icon = "🌙" if self.current_theme == "light" else "☀️"
        theme_text = "Escuro" if self.current_theme == "light" else "Claro"
        if hasattr(self, 'theme_button'):
            self.theme_button.config(text=f"{theme_icon} {theme_text}")
        
    def update_colors(self):
        """Atualiza as cores baseadas no tema atual"""
        theme = self.themes[self.current_theme]
        self.colors = {
            'primary': theme.get('accent', theme['select_bg']),
            'secondary': theme.get('secondary', theme['button_bg']), 
            'success': theme.get('success_fg', '#28a745'),
            'background': theme['bg'],
            'text': theme['fg']
        }
    
    def apply_theme(self):
        """Aplica o tema atual a todos os componentes"""
        if not hasattr(self, 'root'):
            return
            
        theme = self.themes[self.current_theme]
        
        # Atualiza as cores baseadas no tema
        self.update_colors()
        
        # Aplica tema na janela principal
        self.root.configure(bg=theme['bg'])
        
        try:
            # Aplica tema no notebook com melhor estilização
            style = ttk.Style()
            style.theme_use('clam')
            
            # Configura estilos do notebook com cores aprimoradas
            style.configure('TNotebook', 
                           background=theme['bg'],
                           borderwidth=0,
                           tabmargins=[2, 5, 2, 0])
            
            style.configure('TNotebook.Tab', 
                           background=theme['button_bg'], 
                           foreground=theme['button_fg'],
                           padding=[12, 8],
                           borderwidth=1,
                           focuscolor='none')
            
            style.map('TNotebook.Tab', 
                     background=[('selected', theme.get('accent', theme['select_bg'])),
                               ('active', theme.get('hover', theme['button_bg']))],
                     foreground=[('selected', theme['select_fg']),
                               ('active', theme['button_fg'])],
                     borderwidth=[('selected', 2), ('!selected', 1)])
            
            # Configura progressbar se existir
            style.configure('TProgressbar',
                           background=theme.get('accent', theme['select_bg']),
                           troughcolor=theme['entry_bg'],
                           borderwidth=0,
                           lightcolor=theme.get('accent', theme['select_bg']),
                           darkcolor=theme.get('accent', theme['select_bg']))
        except Exception as e:
            # Se houver erro na configuração do estilo, continua sem estilo
            pass
            
        # Aplica tema em todos os widgets filhos
        try:
            self._apply_theme_recursive(self.root, theme)
        except Exception as e:
            # Se houver erro na aplicação recursiva, continua sem aplicar
            pass
        
    def _apply_theme_recursive(self, widget, theme):
        """Aplica tema recursivamente em todos os widgets"""
        try:
            widget_class = widget.winfo_class()
        except:
            # Se não conseguir obter a classe, continua sem aplicar tema
            return
            
        try:
            if widget_class == 'Frame':
                # Verifica se é um frame especial (como status_frame)
                widget.configure(bg=theme['frame_bg'])
            elif widget_class == 'Label':
                # Verifica se é um label especial (título, status, etc.)
                text = widget.cget('text') if hasattr(widget, 'cget') else ''
                if '🏦' in text or 'Organizador' in text:
                    # Título principal com cor de destaque
                    widget.configure(bg=theme['bg'], fg=theme.get('accent', theme['fg']))
                elif 'Status:' in text or 'Progresso:' in text:
                    # Labels de status mantêm fundo do frame pai
                    widget.configure(bg=theme['frame_bg'], fg=theme['fg'])
                else:
                    widget.configure(bg=theme['frame_bg'], fg=theme['fg'])
            elif widget_class == 'Button':
                # Botões com melhor contraste e hover
                widget.configure(
                    bg=theme['button_bg'], 
                    fg=theme['button_fg'], 
                    activebackground=theme.get('hover', theme['select_bg']),
                    activeforeground=theme['button_fg'],
                    relief='flat',
                    borderwidth=1,
                    highlightthickness=0,
                    highlightbackground=theme.get('border', theme['button_bg'])
                )
            elif widget_class == 'Entry':
                widget.configure(
                    bg=theme['entry_bg'], 
                    fg=theme['entry_fg'], 
                    insertbackground=theme['entry_fg'],
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['select_fg'],
                    relief='solid',
                    borderwidth=1,
                    highlightthickness=1,
                    highlightcolor=theme.get('accent', theme['select_bg']),
                    highlightbackground=theme.get('border', theme['entry_bg'])
                )
            elif widget_class == 'Text':
                widget.configure(
                    bg=theme['text_bg'], 
                    fg=theme['text_fg'], 
                    insertbackground=theme['text_fg'],
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['select_fg'],
                    relief='solid',
                    borderwidth=1,
                    highlightthickness=1,
                    highlightcolor=theme.get('accent', theme['select_bg']),
                    highlightbackground=theme.get('border', theme['text_bg'])
                )
            elif widget_class == 'Listbox':
                widget.configure(
                    bg=theme['entry_bg'], 
                    fg=theme['entry_fg'], 
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['select_fg'],
                    relief='solid',
                    borderwidth=1,
                    highlightthickness=1,
                    highlightcolor=theme.get('accent', theme['select_bg']),
                    highlightbackground=theme.get('border', theme['entry_bg'])
                )
            elif widget_class == 'Scrollbar':
                widget.configure(
                    bg=theme['button_bg'], 
                    troughcolor=theme['frame_bg'],
                    activebackground=theme.get('hover', theme['button_bg']),
                    relief='flat',
                    borderwidth=0
                )
            elif widget_class == 'Spinbox':
                widget.configure(
                    bg=theme['entry_bg'],
                    fg=theme['entry_fg'],
                    insertbackground=theme['entry_fg'],
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['select_fg'],
                    buttonbackground=theme['button_bg'],
                    relief='solid',
                    borderwidth=1,
                    highlightthickness=1,
                    highlightcolor=theme.get('accent', theme['select_bg'])
                )
        except Exception as e:
            # Ignora erros de configuração mas pode logar para debug
            pass
            
        # Aplica recursivamente aos filhos
        try:
            for child in widget.winfo_children():
                self._apply_theme_recursive(child, theme)
        except Exception as e:
            # Se houver erro ao obter filhos, continua
            pass
        
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
        
    def view_checkpoint(self):
        """Exibe os detalhes do checkpoint atual"""
        checkpoint_data = self.load_checkpoint()
        
        if not checkpoint_data:
            messagebox.showinfo("Checkpoint", "Nenhum checkpoint encontrado!")
            return
        
        # Cria janela para exibir detalhes
        checkpoint_window = Toplevel(self.root)
        checkpoint_window.title("📋 Detalhes do Checkpoint")
        checkpoint_window.geometry("600x500")
        checkpoint_window.resizable(True, True)
        
        # Aplica tema à janela
        theme = self.themes[self.current_theme]
        checkpoint_window.configure(bg=theme['bg'])
        
        # Frame principal com scroll
        main_frame = Frame(checkpoint_window, bg=theme['bg'])
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = Label(main_frame, text="📋 Informações do Checkpoint",
                           font=("Arial", 14, "bold"), bg=theme['bg'], fg=theme['accent'])
        title_label.pack(pady=(0, 15))
        
        # Área de texto com scroll
        text_frame = Frame(main_frame, bg=theme['bg'])
        text_frame.pack(fill=BOTH, expand=True)
        
        text_widget = scrolledtext.ScrolledText(text_frame, 
                                               bg=theme['text_bg'], 
                                               fg=theme['text_fg'],
                                               font=("Consolas", 10),
                                               wrap=WORD)
        text_widget.pack(fill=BOTH, expand=True)
        
        # Formata e exibe os dados
        info_text = self._format_checkpoint_info(checkpoint_data)
        text_widget.insert(END, info_text)
        text_widget.config(state=DISABLED)
        
        # Botão fechar
        close_button = Button(main_frame, text="✖️ Fechar",
                             command=checkpoint_window.destroy,
                             bg=theme['button_bg'], fg=theme['button_fg'],
                             font=("Arial", 10))
        close_button.pack(pady=(10, 0))
        
        # Centraliza a janela
        checkpoint_window.transient(self.root)
        checkpoint_window.grab_set()
        
    def _format_checkpoint_info(self, checkpoint_data):
        """Formata as informações do checkpoint para exibição"""
        timestamp = checkpoint_data.get('timestamp', 'Desconhecido')
        try:
            # Converte timestamp para formato legível
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%d/%m/%Y às %H:%M:%S')
        except:
            formatted_time = timestamp
        
        current_index = checkpoint_data.get('current_index', 0)
        total_files = checkpoint_data.get('total_files', 0)
        base_dir = checkpoint_data.get('base_directory', 'N/A')
        output_dir = checkpoint_data.get('output_directory', 'N/A')
        stats = checkpoint_data.get('stats', {})
        files = checkpoint_data.get('files', [])
        api_keys_count = checkpoint_data.get('api_keys_count', 0)
        current_api_index = checkpoint_data.get('current_api_index', 0)
        
        info = f"""🕒 INFORMAÇÕES GERAIS
{'='*50}
📅 Data/Hora: {formatted_time}
📁 Diretório Base: {base_dir}
📂 Diretório Saída: {output_dir}
🔑 Chaves API: {api_keys_count} (atual: {current_api_index + 1})

📊 PROGRESSO
{'='*50}
📄 Arquivo Atual: {current_index + 1} de {total_files}
📈 Progresso: {(current_index/total_files*100):.1f}% concluído
⏳ Arquivos Restantes: {total_files - current_index}

📈 ESTATÍSTICAS
{'='*50}
✅ Sucessos: {stats.get('success', 0)}
❌ Erros: {stats.get('errors', 0)}
📊 Total Processados: {stats.get('success', 0) + stats.get('errors', 0)}

🏦 POR BANCO
{'='*50}
"""
        
        # Adiciona estatísticas por banco
        by_bank = stats.get('by_bank', {})
        if by_bank:
            for bank, count in by_bank.items():
                info += f"• {bank}: {count} arquivo(s)\n"
        else:
            info += "Nenhum dado por banco ainda\n"
        
        info += f"\n📅 POR MÊS\n{'='*50}\n"
        
        # Adiciona estatísticas por mês
        by_month = stats.get('by_month', {})
        if by_month:
            for month, count in sorted(by_month.items()):
                info += f"• {month}: {count} arquivo(s)\n"
        else:
            info += "Nenhum dado por mês ainda\n"
        
        info += f"\n📋 ARQUIVOS A PROCESSAR\n{'='*50}\n"
        
        # Lista próximos arquivos
        remaining_files = files[current_index:current_index+10]  # Mostra próximos 10
        for i, file_path in enumerate(remaining_files):
            status = "➡️ PRÓXIMO" if i == 0 else "⏳ PENDENTE"
            file_name = os.path.basename(file_path)
            info += f"{status} {file_name}\n"
        
        if len(files) > current_index + 10:
            remaining = len(files) - current_index - 10
            info += f"... e mais {remaining} arquivo(s)\n"
        
        return info
    
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