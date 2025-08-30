# 📖 Manual do Projeto - Organizador de Extratos Bancários

Este manual descreve detalhadamente o propósito e funcionamento de cada arquivo no projeto **Organizador de Extratos Bancários**.

## 📁 Arquivos Principais

### `organizador_extratos_gui.py`
- **Tipo**: Script Python principal.
- **Propósito**: Contém toda a lógica da aplicação e a interface gráfica (GUI) baseada em `tkinter`.
- **Detalhes**:
  - Implementa a classe `OrganizadorExtratosGUI` que gerencia as 3 abas da interface.
  - Realiza a extração de texto de PDFs (com `PyPDF2`) e OFX.
  - Integra com a API do Google Qwen para análise inteligente dos documentos.
  - Organiza os arquivos em uma estrutura de pastas baseada em ano, mês, instituição e tipo de conta.
  - Gerencia preferências do usuário e checkpoints para retomar processos interrompidos.
  - Utiliza funções auxiliares para compatibilidade com executáveis PyInstaller (`get_base_path`, `get_resource_path`).

### `executar_gui.bat`
- **Tipo**: Script batch (Windows).
- **Propósito**: Script de inicialização para o usuário final.
- **Detalhes**:
  - Verifica se o Python está instalado.
  - Confirma a existência do arquivo principal `organizador_extratos_gui.py`.
  - Verifica e instala automaticamente as dependências (`google-generativeai`, `PyPDF2`) se necessário.
  - Executa a aplicação GUI.
  - Fornece mensagens de erro e dicas úteis.

### `build_executable.py`
- **Tipo**: Script Python de build.
- **Propósito**: Automatiza a criação de um executável standalone usando `PyInstaller`.
- **Detalhes**:
  - Verifica e instala `PyInstaller` se não estiver presente.
  - Cria um arquivo de especificação `.spec` personalizado para o PyInstaller.
  - Gera o executável em `dist/OrganizadorExtratos.exe`.
  - Cria uma pasta de distribuição `Distribuicao` com o executável, `README.md` e um arquivo de instruções.

### `setup.py`
- **Tipo**: Script de configuração Python setuptools.
- **Propósito**: Define metadados do projeto e dependências para empacotamento e distribuição.
- **Detalhes**:
  - Lê `README.md` para a descrição longa.
  - Lê `requirements.txt` para as dependências principais.
  - Configura classificadores, versão, autor, etc.
  - Define `entry_points` para possíveis scripts de console (embora a GUI seja o foco).
  - Inclui ` extras_require ` para dependências de desenvolvimento e build.

### `requirements.txt`
- **Tipo**: Arquivo de texto.
- **Propósito**: Lista as dependências Python necessárias para o projeto.
- **Detalhes**:
  - Inclui `google-generativeai` e `PyPDF2` como dependências principais.
  - Inclui `pyinstaller` como dependência de build.
  - Menciona bibliotecas built-in do Python que são utilizadas.

### `logger_config.py`
- **Tipo**: Script Python auxiliar.
- **Propósito**: Configura o sistema de logging da aplicação.
- **Detalhes**:
  - Cria um logger com handlers para console e arquivo.
  - Salva logs na pasta `.organizador_extratos/logs` no diretório home do usuário.
  - Formata as mensagens de log com data, nome do logger, nível e mensagem.

### `README.md`
- **Tipo**: Arquivo Markdown.
- **Propósito**: Documentação principal do projeto.
- **Detalhes**:
  - Explica o objetivo, funcionalidades e vantagens da versão GUI.
  - Fornece instruções de início rápido, requisitos e solução de problemas.
  - Inclui capturas de tela descritivas das abas da interface.
  - Detalha a estrutura de pastas de organização e aspectos de privacidade.

## 📁 Arquivos de Configuração e Recursos

### `app.manifest`
- **Tipo**: Arquivo XML de manifesto do Windows.
- **Propósito**: Define configurações de compatibilidade e privilégios para o executável.
- **Detalhes**:
  - Especifica que o programa requer execução como administrador (isso pode ser um ponto de atenção para distribuição).
  - Define compatibilidade com versões do Windows.

### `icon.ico` (se presente)
- **Tipo**: Arquivo de ícone.
- **Propósito**: Ícone principal da aplicação.
- **Detalhes**:
  - Utilizado pelo `build_executable.py` durante a criação do .exe.
  - Deve ter dimensões adequadas (ex: 32x32, 64x64 pixels).

### `ICON_INFO.txt`
- **Tipo**: Arquivo de texto.
- **Propósito**: Fornece informações sobre o ícone do projeto.
- **Detalhes**:
  - Criado pelo `build_executable.py` como um placeholder.
  - Contém instruções sobre como adicionar um ícone personalizado para o executável.

## 📁 Outros Arquivos

### `QWEN.md` (este arquivo)
- **Tipo**: Arquivo Markdown.
- **Propósito**: Contexto gerado para uso com Qwen Code.
- **Detalhes**:
  - Resumo técnico do projeto para assistência automatizada.

### `.gitignore`
- **Tipo**: Arquivo de configuração Git.
- **Propósito**: Especifica arquivos e pastas que devem ser ignorados pelo Git.
- **Detalhes**:
  - Geralmente inclui pastas de build (`dist/`, `build/`), arquivos temporários e logs.

### `.git`
- **Tipo**: Diretório do Git.
- **Propósito**: Contém metadados do repositório Git.