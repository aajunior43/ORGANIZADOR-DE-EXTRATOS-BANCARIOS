# 📦 Guia de Distribuição do Executável

## 🎯 Como Criar o Executável

### Método 1: Script Automático (Recomendado)
1. **Duplo clique em:** `criar_executavel.bat`
2. **Escolha opção 1:** "Criar executável (automático)"
3. **Aguarde:** O processo pode demorar 5-10 minutos
4. **Resultado:** Pasta `Distribuicao` com o executável pronto

### Método 2: Manual
1. **Instale dependências:**
   ```bash
   pip install pyinstaller>=5.0.0
   ```

2. **Execute o build:**
   ```bash
   python build_executable.py
   ```

## 📁 Estrutura da Distribuição

Após o build, você terá:
```
Distribuicao/
├── OrganizadorExtratos.exe    # Executável principal
├── README.md                  # Documentação
└── INSTRUÇÕES.txt            # Guia rápido de uso
```

## 🚀 Como Distribuir

### ✅ O que Incluir
- **Pasta completa `Distribuicao`**
- **Todos os arquivos** dentro da pasta
- **Instruções de uso** (já incluídas)

### ❌ O que NÃO Incluir
- Arquivos `.py` (código fonte)
- Pasta `build/` (temporária)
- Pasta `dist/` (temporária)
- Arquivos `.spec` (configuração de build)

## 💻 Requisitos do Sistema de Destino

### ✅ Necessário
- **Windows 7** ou superior
- **4 GB RAM** mínimo (8 GB recomendado)
- **500 MB** espaço livre em disco
- **Conexão com internet** (para API do Gemini)

### ❌ NÃO Necessário
- Python instalado
- Dependências Python
- Configuração adicional

## 🛡️ Segurança e Antivírus

### ⚠️ Possíveis Alertas
Alguns antivírus podem alertar sobre o executável porque:
- É um arquivo novo/desconhecido
- PyInstaller empacota muitas bibliotecas
- Acessa arquivos do sistema (normal para organizar extratos)

### ✅ Como Resolver
1. **Adicione exceção** no antivírus
2. **Escaneie o arquivo** em sites como VirusTotal
3. **Distribua o código fonte** junto (transparência)

## 📋 Checklist de Distribuição

### Antes de Distribuir
- [ ] Testou o executável em computador limpo
- [ ] Verificou se todas as funcionalidades funcionam
- [ ] Incluiu documentação adequada
- [ ] Testou com diferentes tipos de extratos

### Ao Distribuir
- [ ] Compactou a pasta `Distribuicao` em ZIP
- [ ] Incluiu instruções de instalação
- [ ] Forneceu informações de suporte
- [ ] Explicou requisitos do sistema

## 🔧 Solução de Problemas

### "Executável não abre"
**Possíveis causas:**
- Antivírus bloqueando
- Falta de permissões
- Sistema incompatível

**Soluções:**
1. Executar como administrador
2. Adicionar exceção no antivírus
3. Verificar compatibilidade do Windows

### "Erro de DLL faltando"
**Solução:**
- Instalar Visual C++ Redistributable
- Baixar em: https://aka.ms/vs/17/release/vc_redist.x64.exe

### "Interface não aparece corretamente"
**Solução:**
- Ajustar configurações de DPI do Windows
- Clicar com botão direito no executável > Propriedades > Compatibilidade

## 📞 Suporte ao Usuário Final

### Informações para Incluir
```
🏦 ORGANIZADOR DE EXTRATOS BANCÁRIOS

📋 REQUISITOS:
- Windows 7 ou superior
- Conexão com internet
- Chave gratuita do Google Gemini

🚀 COMO USAR:
1. Execute OrganizadorExtratos.exe
2. Configure sua chave da API na primeira aba
3. Selecione a pasta com seus extratos
4. Clique "Iniciar Organização"

🛡️ SEGURANÇA:
- Seus arquivos originais NUNCA são alterados
- Apenas cópias são organizadas
- Processamento local e seguro

📞 SUPORTE:
- Consulte README.md para detalhes
- Use "Salvar Log" em caso de problemas
```

## 🎯 Dicas de Distribuição

### Para Usuários Técnicos
- Inclua código fonte para transparência
- Forneça hash MD5/SHA256 do executável
- Disponibilize logs de build

### Para Usuários Finais
- Crie vídeo tutorial simples
- Forneça exemplos de extratos
- Inclua FAQ com problemas comuns

### Para Empresas
- Teste em ambiente corporativo
- Verifique políticas de segurança
- Considere assinatura digital do executável

## 📈 Melhorias Futuras

### Possíveis Adições
- [ ] Instalador MSI/NSIS
- [ ] Assinatura digital
- [ ] Auto-update
- [ ] Versão portable
- [ ] Suporte a mais bancos

---

**🎉 Seu organizador está pronto para distribuição profissional!**