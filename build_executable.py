#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔨 Script de Build para Executável
Organizador de Extratos Bancários

Este script automatiza a criação do executável usando PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Verifica se PyInstaller está instalado"""
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
        return True
    except ImportError:
        print("❌ PyInstaller não encontrado")
        print("📦 Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller instalado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar PyInstaller")
            return False

def create_spec_file():
    """Cria arquivo .spec personalizado para PyInstaller"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['organizador_extratos_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'google.generativeai',
        'google.ai.generativelanguage',
        'google.api_core',
        'google.auth',
        'PyPDF2',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.font',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OrganizadorExtratos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sem console para interface gráfica
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('organizador_extratos.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Arquivo .spec criado")

def create_icon():
    """Cria um ícone simples em formato ICO"""
    # Como não podemos criar um ICO real aqui, criamos um placeholder
    icon_info = """
# Para adicionar um ícone personalizado:
# 1. Crie ou baixe um arquivo .ico (32x32 ou 64x64 pixels)
# 2. Renomeie para 'icon.ico'
# 3. Coloque na pasta do projeto
# 4. Execute novamente o build
"""
    
    with open('ICON_INFO.txt', 'w', encoding='utf-8') as f:
        f.write(icon_info)
    
    print("📝 Informações sobre ícone criadas em ICON_INFO.txt")

def build_executable():
    """Constrói o executável"""
    print("🔨 Iniciando build do executável...")
    
    try:
        # Limpa builds anteriores
        if os.path.exists('build'):
            shutil.rmtree('build')
            print("🗑️ Pasta build anterior removida")
        
        if os.path.exists('dist'):
            shutil.rmtree('dist')
            print("🗑️ Pasta dist anterior removida")
        
        # Executa PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "organizador_extratos.spec"
        ]
        
        print(f"🚀 Executando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build concluído com sucesso!")
            
            # Verifica se o executável foi criado
            exe_path = Path('dist/OrganizadorExtratos.exe')
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Executável criado: {exe_path}")
                print(f"📊 Tamanho: {size_mb:.1f} MB")
                
                # Cria pasta de distribuição
                dist_folder = Path('Distribuicao')
                if dist_folder.exists():
                    shutil.rmtree(dist_folder)
                
                dist_folder.mkdir()
                
                # Copia executável
                shutil.copy2(exe_path, dist_folder / 'OrganizadorExtratos.exe')
                
                # Copia documentação
                if Path('README.md').exists():
                    shutil.copy2('README.md', dist_folder / 'README.md')
                
                # Cria arquivo de instruções
                instructions = """
🏦 ORGANIZADOR DE EXTRATOS BANCÁRIOS
=====================================

📋 INSTRUÇÕES DE USO:

1. 🔑 CONFIGURE A API:
   - Execute OrganizadorExtratos.exe
   - Na aba "Configuração", clique em "Obter Chave"
   - Gere uma chave gratuita do Google Gemini
   - Cole a chave e clique "Adicionar"

2. 📁 SELECIONE SEUS EXTRATOS:
   - Clique em "Selecionar" para escolher a pasta
   - Clique em "Escanear Arquivos"

3. 🚀 ORGANIZE:
   - Vá para aba "Processamento"
   - Clique "Iniciar Organização"
   - Acompanhe o progresso

4. 📊 VEJA RESULTADOS:
   - Aba "Resultados" mostra estatísticas
   - Botão "Abrir Pasta Organizada"

🛡️ SEGURANÇA:
- Seus arquivos originais NUNCA são alterados
- Apenas cópias são organizadas
- Verificação de integridade automática

📞 SUPORTE:
- Consulte README.md para mais detalhes
- Use "Salvar Log" em caso de problemas

🎉 Aproveite seu organizador de extratos!
"""
                
                with open(dist_folder / 'INSTRUÇÕES.txt', 'w', encoding='utf-8') as f:
                    f.write(instructions)
                
                print(f"📁 Pasta de distribuição criada: {dist_folder.absolute()}")
                print("📋 Arquivos incluídos:")
                for item in dist_folder.iterdir():
                    print(f"   - {item.name}")
                
                return True
            else:
                print("❌ Executável não encontrado após build")
                return False
        else:
            print("❌ Erro durante o build:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    print("🔨 BUILD DO ORGANIZADOR DE EXTRATOS")
    print("="*50)
    
    # Verifica se estamos no diretório correto
    if not Path('organizador_extratos_gui.py').exists():
        print("❌ Arquivo organizador_extratos_gui.py não encontrado!")
        print("💡 Execute este script na pasta do projeto")
        return False
    
    # Verifica PyInstaller
    if not check_pyinstaller():
        return False
    
    # Cria arquivos necessários
    create_spec_file()
    create_icon()
    
    # Constrói executável
    success = build_executable()
    
    if success:
        print("\n🎉 BUILD CONCLUÍDO COM SUCESSO!")
        print("\n📦 PRÓXIMOS PASSOS:")
        print("   1. Teste o executável na pasta 'Distribuicao'")
        print("   2. Distribua a pasta completa para outros usuários")
        print("   3. Não é necessário instalar Python no computador de destino")
        print("\n✨ Seu organizador está pronto para distribuição!")
    else:
        print("\n❌ BUILD FALHOU")
        print("💡 Verifique os erros acima e tente novamente")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Build interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPressione Enter para sair...")