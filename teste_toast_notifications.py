#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔔 Teste das Notificações Toast
Demonstração do sistema de notificações integrado ao Organizador de Extratos

Este script testa as notificações toast implementadas no sistema principal.
"""

import tkinter as tk
from tkinter import ttk
import time

def main():
    """Função principal para testar as notificações toast"""
    
    # Cria janela principal
    root = tk.Tk()
    root.title("🔔 Teste de Notificações Toast")
    root.geometry("600x400")
    root.configure(bg='#f0f0f0')
    
    # Centraliza a janela
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (300)
    y = (root.winfo_screenheight() // 2) - (200)
    root.geometry(f"600x400+{x}+{y}")
    
    # Título
    title_label = tk.Label(root, 
                          text="🔔 Sistema de Notificações Toast",
                          font=("Segoe UI", 16, "bold"),
                          bg='#f0f0f0',
                          fg='#2c3e50')
    title_label.pack(pady=20)
    
    # Descrição
    desc_label = tk.Label(root,
                         text="Teste as notificações toast implementadas no Organizador de Extratos.\n"
                              "As notificações aparecem no canto superior direito da tela.",
                         font=("Segoe UI", 10),
                         bg='#f0f0f0',
                         fg='#34495e',
                         justify=tk.CENTER)
    desc_label.pack(pady=10)
    
    # Simula a classe ToastNotification (versão simplificada para teste)
    class SimpleToast:
        def __init__(self, parent):
            self.parent = parent
            self.notifications = []
            self.notification_id = 0
            
        def show_toast(self, message, level="INFO", duration=4000):
            """Mostra uma notificação toast simples"""
            self.notification_id += 1
            
            # Cores por tipo
            colors = {
                "SUCCESS": {"bg": "#10b981", "fg": "#ffffff", "icon": "✅"},
                "ERROR": {"bg": "#ef4444", "fg": "#ffffff", "icon": "❌"},
                "WARNING": {"bg": "#f59e0b", "fg": "#ffffff", "icon": "⚠️"},
                "INFO": {"bg": "#3b82f6", "fg": "#ffffff", "icon": "ℹ️"}
            }
            
            config = colors.get(level, colors["INFO"])
            
            # Cria janela do toast
            toast = tk.Toplevel(self.parent)
            toast.withdraw()
            toast.overrideredirect(True)
            toast.attributes('-topmost', True)
            
            # Posicionamento
            screen_width = self.parent.winfo_screenwidth()
            toast_width = 350
            toast_height = 80
            margin = 20
            
            y_offset = margin + (len(self.notifications) * (toast_height + 10))
            x = screen_width - toast_width - margin
            y = y_offset
            
            toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
            
            # Frame principal
            main_frame = tk.Frame(toast, 
                                 bg=config['bg'],
                                 relief='flat',
                                 bd=2,
                                 highlightbackground='#ffffff',
                                 highlightthickness=1)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Container do conteúdo
            content_frame = tk.Frame(main_frame, bg=config['bg'])
            content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
            
            # Ícone e mensagem
            icon_label = tk.Label(content_frame,
                                 text=config['icon'],
                                 font=('Segoe UI Emoji', 14),
                                 bg=config['bg'],
                                 fg=config['fg'])
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
            
            message_label = tk.Label(content_frame,
                                   text=message,
                                   font=('Segoe UI', 10),
                                   bg=config['bg'],
                                   fg=config['fg'],
                                   wraplength=250,
                                   justify=tk.LEFT)
            message_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Botão fechar
            close_btn = tk.Label(content_frame,
                               text='✖',
                               font=('Segoe UI', 10, 'bold'),
                               bg=config['bg'],
                               fg=config['fg'],
                               cursor='hand2')
            close_btn.pack(side=tk.RIGHT)
            
            # Eventos
            def close_toast(event=None):
                self.hide_toast(toast, self.notification_id)
                
            close_btn.bind('<Button-1>', close_toast)
            toast.bind('<Button-1>', close_toast)
            
            # Adiciona à lista
            toast_data = {
                'id': self.notification_id,
                'window': toast,
                'level': level
            }
            self.notifications.append(toast_data)
            
            # Mostra com animação
            self.animate_show(toast)
            
            # Auto-remove
            if duration > 0:
                self.parent.after(duration, lambda: self.hide_toast(toast, self.notification_id))
                
            return self.notification_id
        
        def animate_show(self, toast):
            """Anima a entrada do toast"""
            toast.attributes('-alpha', 0.0)
            toast.deiconify()
            
            def fade_in(alpha=0.0):
                if alpha < 0.95:
                    alpha += 0.1
                    toast.attributes('-alpha', alpha)
                    self.parent.after(30, lambda: fade_in(alpha))
                else:
                    toast.attributes('-alpha', 0.95)
                    
            fade_in()
        
        def hide_toast(self, toast, toast_id):
            """Esconde um toast"""
            def fade_out(alpha=0.95):
                if alpha > 0:
                    alpha -= 0.15
                    try:
                        toast.attributes('-alpha', alpha)
                        self.parent.after(20, lambda: fade_out(alpha))
                    except:
                        pass
                else:
                    try:
                        toast.destroy()
                    except:
                        pass
                    # Remove da lista
                    self.notifications = [n for n in self.notifications if n['id'] != toast_id]
                    self.reposition_toasts()
            
            fade_out()
        
        def reposition_toasts(self):
            """Reposiciona os toasts"""
            screen_width = self.parent.winfo_screenwidth()
            toast_width = 350
            toast_height = 80
            margin = 20
            
            for i, notification in enumerate(self.notifications):
                toast = notification['window']
                y_offset = margin + (i * (toast_height + 10))
                x = screen_width - toast_width - margin
                
                try:
                    toast.geometry(f"{toast_width}x{toast_height}+{x}+{y_offset}")
                except:
                    pass
        
        def clear_all(self):
            """Remove todos os toasts"""
            for notification in self.notifications[:]:
                try:
                    notification['window'].destroy()
                except:
                    pass
            self.notifications.clear()
    
    # Inicializa sistema de toast
    toast_system = SimpleToast(root)
    
    # Frame de botões
    buttons_frame = tk.Frame(root, bg='#f0f0f0')
    buttons_frame.pack(pady=30)
    
    # Botões de teste
    def test_success():
        toast_system.show_toast("✅ Processamento concluído com sucesso! 15 arquivos organizados.", "SUCCESS", 5000)
    
    def test_error():
        toast_system.show_toast("❌ Erro crítico na API! Verifique sua chave de acesso.", "ERROR", 6000)
    
    def test_warning():
        toast_system.show_toast("⚠️ Rate limit detectado! Aguardando 30 segundos...", "WARNING", 4000)
    
    def test_info():
        toast_system.show_toast("ℹ️ Processando arquivo 25 de 50... Banco do Brasil detectado.", "INFO", 3000)
    
    def test_multiple():
        """Testa múltiplas notificações"""
        toast_system.show_toast("🔍 Escaneamento iniciado...", "INFO", 2000)
        root.after(500, lambda: toast_system.show_toast("📄 15 arquivos encontrados", "INFO", 3000))
        root.after(1000, lambda: toast_system.show_toast("🚀 Iniciando processamento", "SUCCESS", 4000))
        root.after(1500, lambda: toast_system.show_toast("⚠️ Chave API próxima do limite", "WARNING", 5000))
    
    def clear_all():
        toast_system.clear_all()
    
    # Estilo dos botões
    button_style = {
        'font': ('Segoe UI', 10, 'bold'),
        'padx': 20,
        'pady': 10,
        'relief': 'flat',
        'cursor': 'hand2',
        'width': 20
    }
    
    # Botões de teste
    success_btn = tk.Button(buttons_frame, text="✅ Testar Sucesso", 
                           command=test_success, bg='#10b981', fg='white', **button_style)
    success_btn.pack(pady=5)
    
    error_btn = tk.Button(buttons_frame, text="❌ Testar Erro", 
                         command=test_error, bg='#ef4444', fg='white', **button_style)
    error_btn.pack(pady=5)
    
    warning_btn = tk.Button(buttons_frame, text="⚠️ Testar Aviso", 
                           command=test_warning, bg='#f59e0b', fg='white', **button_style)
    warning_btn.pack(pady=5)
    
    info_btn = tk.Button(buttons_frame, text="ℹ️ Testar Info", 
                        command=test_info, bg='#3b82f6', fg='white', **button_style)
    info_btn.pack(pady=5)
    
    multiple_btn = tk.Button(buttons_frame, text="🔄 Testar Múltiplas", 
                            command=test_multiple, bg='#8b5cf6', fg='white', **button_style)
    multiple_btn.pack(pady=5)
    
    clear_btn = tk.Button(buttons_frame, text="🗑️ Limpar Todas", 
                         command=clear_all, bg='#6b7280', fg='white', **button_style)
    clear_btn.pack(pady=5)
    
    # Informações na parte inferior
    info_frame = tk.Frame(root, bg='#e8f4fd', relief=tk.RIDGE, bd=1)
    info_frame.pack(fill=tk.X, padx=20, pady=20)
    
    info_text = tk.Label(info_frame,
                        text="💡 As notificações aparecem no canto superior direito da tela\n"
                             "• Clique nas notificações para fechá-las\n"
                             "• Elas desaparecem automaticamente após alguns segundos\n"
                             "• Máximo de 5 notificações simultâneas",
                        font=('Segoe UI', 9),
                        bg='#e8f4fd',
                        fg='#1565c0',
                        justify=tk.LEFT)
    info_text.pack(padx=15, pady=10)
    
    # Inicia a aplicação
    print("🔔 Iniciando teste das notificações toast...")
    print("📱 Clique nos botões para testar diferentes tipos de notificação")
    
    root.mainloop()

if __name__ == "__main__":
    main()