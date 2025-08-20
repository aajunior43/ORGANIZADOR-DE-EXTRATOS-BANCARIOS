# 🏦 Organizador de Extratos Bancários - Interface Gráfica

**Versão 2.0 com Interface Gráfica Moderna**

Programa inteligente com interface visual que organiza automaticamente seus extratos bancários (PDF e OFX) usando inteligência artificial Google Gemini.

![Interface](https://img.shields.io/badge/Interface-Gráfica-blue) ![IA](https://img.shields.io/badge/IA-Gemini-green) ![Python](https://img.shields.io/badge/Python-3.8+-yellow)

## 🚀 Início Rápido

### 1️⃣ Executar o Programa
**Duplo clique em:** `executar_gui.bat`

Ou manualmente:
```bash
pip install google-generativeai PyPDF2
python organizador_extratos_gui.py
```

### 2️⃣ Configurar na Interface
1. **Aba "Configuração":**
   - Cole sua chave da API do Gemini (obtenha em: https://makersuite.google.com/app/apikey)
   - Selecione a pasta com seus extratos
   - Clique em "Escanear Arquivos"

2. **Aba "Processamento":**
   - Clique em "Iniciar Organização"
   - Acompanhe o progresso em tempo real

3. **Aba "Resultados":**
   - Veja estatísticas detalhadas
   - Abra a pasta organizada
   - Salve o log do processamento

## 🎯 Funcionalidades

### ✨ Interface Moderna
- **3 Abas Organizadas**: Configuração, Processamento e Resultados
- **Progresso Visual**: Barra de progresso e log colorido em tempo real
- **Controles Intuitivos**: Botões grandes e interface amigável
- **Feedback Imediato**: Status e mensagens claras

### 🤖 IA Avançada
- **Análise Inteligente**: Identifica banco, mês, ano e tipo de conta automaticamente
- **3 Tentativas por Arquivo**: Garante máxima precisão
- **Fallback Inteligente**: Análise por nome se IA falhar
- **Intervalo de 10 segundos**: Entre cada arquivo para não sobrecarregar a API

### 📁 Organização Automática
```
EXTRATOS_ORGANIZADOS/
├── 2024/
│   ├── 04_ABRIL/
│   │   ├── CAIXA/
│   │   │   ├── CORRENTE/
│   │   │   │   ├── PDF/
│   │   │   │   └── OFX/
│   │   │   ├── POUPANCA/
│   │   │   └── INVESTIMENTO/
│   │   └── BANCO_DO_BRASIL/
│   └── 03_MARÇO/
└── 2023/
```

### 📊 Relatórios Detalhados
- **Estatísticas por Banco**: Quantos arquivos de cada instituição
- **Estatísticas por Mês**: Distribuição temporal
- **Log Completo**: Histórico detalhado de cada operação
- **Exportação**: Salve relatórios em arquivo

## 🖼️ Capturas de Tela

### Aba Configuração
- ✅ Campo para chave da API com botão "Testar"
- 📁 Seletor de pasta com preview dos arquivos
- 🔍 Contador de arquivos encontrados

### Aba Processamento
- 🚀 Botões grandes "Iniciar" e "Parar"
- 📊 Barra de progresso visual
- 📋 Log colorido em tempo real

### Aba Resultados
- 📈 Estatísticas organizadas
- 🔧 Botões para abrir pasta e salvar log
- 🔄 Opção de novo processamento

## ⚙️ Requisitos

- **Python 3.8+**
- **Chave da API Google Gemini** (gratuita)
- **Conexão com internet** (para análise IA)
- **Windows** (testado no Windows 10/11)

## 📈 Performance

- **Velocidade**: 1 arquivo a cada 10 segundos
- **Precisão**: Até 3 tentativas de IA por arquivo
- **Capacidade**: Processa centenas de arquivos automaticamente
- **Memória**: Otimizado para arquivos grandes

## 🛠️ Solução de Problemas

### ❌ "Dependências Faltando"
**Solução**: Execute `executar_gui.bat` que instala automaticamente

### ❌ "Erro de API"
**Solução**: 
1. Verifique se a chave está correta
2. Use o botão "Testar" na interface
3. Obtenha nova chave em: https://makersuite.google.com/app/apikey

### ❌ "Nenhum arquivo encontrado"
**Solução**:
1. Verifique se selecionou a pasta correta
2. Certifique-se de que há arquivos .pdf ou .ofx
3. Use o botão "Escanear Arquivos"

### ⚠️ "Processamento lento"
**Normal**: O programa aguarda 10 segundos entre arquivos para garantir análise IA completa

## 🔒 Privacidade e Segurança

- ✅ **Processamento Local**: Arquivos ficam no seu computador
- ✅ **Dados Mínimos**: Apenas texto extraído é enviado para IA
- ✅ **Originais Intactos**: Programa copia, não move arquivos
- ✅ **Sem Armazenamento**: Nada é salvo externamente

## 📞 Suporte

### Recursos de Ajuda na Interface:
- **Status em Tempo Real**: Barra inferior mostra status atual
- **Log Detalhado**: Aba de processamento mostra cada etapa
- **Mensagens de Erro**: Alertas claros sobre problemas
- **Botão "Testar API"**: Verifica conectividade

### Arquivos de Log:
- Use "Salvar Log" na aba Resultados
- Contém histórico completo do processamento
- Útil para diagnóstico de problemas

## 🎉 Vantagens da Versão GUI

✅ **Mais Fácil**: Interface visual intuitiva  
✅ **Mais Seguro**: Validações em tempo real  
✅ **Mais Informativo**: Feedback visual constante  
✅ **Mais Controle**: Botões para parar/continuar  
✅ **Mais Organizado**: Abas separadas por função  
✅ **Mais Profissional**: Design moderno e limpo  

---

**🚀 Desenvolvido com Python + tkinter + Google Gemini AI**

*Transforme a organização dos seus extratos bancários em uma experiência visual e intuitiva!*