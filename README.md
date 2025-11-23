
# Motus.IA - Microsserviço de Inteligência e Conteúdo

Este repositório contém o código-fonte do microsserviço de inteligência da **Motus.IA**, uma plataforma de educação adaptativa B2B-ESG focada em combater o *Skills Gap* (lacuna de competências).

## 1. Sobre o Módulo

Este microsserviço atua como o cérebro do Motus.IA, sendo responsável por duas funções críticas:

1.  **Geração de Conteúdo com IA:** Utiliza Modelos de Linguagem Grandes (LLMs), como o Google Gemini, para criar dinamicamente conteúdo educacional personalizado. O material é adaptado em três níveis de complexidade (Básico, Médio e Avançado) para atender às necessidades individuais de cada aluno.
2.  **CMS e Persistência:** Funciona como um Sistema de Gerenciamento de Conteúdo (CMS) que persiste todos os dados gerados em um banco de dados Oracle, garantindo a integridade e a disponibilidade das informações.

O conteúdo gerado é focado no desenvolvimento de competências essenciais para o futuro do trabalho, mapeadas pelo **Fórum Econômico Mundial**, como pensamento analítico, criatividade e resolução de problemas complexos.

## 2. Dependências

Para executar este projeto, as seguintes bibliotecas externas são necessárias:

*   `google-generativeai`: Para integração com a API do Google Gemini.
*   `oracledb`: Driver oficial para conexão com o banco de dados Oracle.
*   `python-dotenv`: Para gerenciamento de variáveis de ambiente.

## 3. Guia de Instalação e Configuração

Siga os passos abaixo para configurar e executar o projeto em um ambiente local.

### Passo 1: Criar e Ativar um Ambiente Virtual

É uma boa prática isolar as dependências do projeto usando um ambiente virtual (`venv`).

```bash
# Crie o ambiente virtual (substitua 'venv' pelo nome que preferir)
python -m venv venv

# Ative o ambiente virtual
# No Windows:
.\venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
```

### Passo 2: Instalar as Dependências

Com o ambiente virtual ativado, instale os pacotes necessários usando o `pip`.

```bash
pip install google-generativeai oracledb python-dotenv
```

### Passo 3: Configurar Variáveis de Ambiente

Este sistema requer um arquivo `.env` na raiz do projeto para armazenar credenciais e configurações sensíveis.

1.  Crie um arquivo chamado `.env` na pasta raiz do projeto.
2.  Copie e cole o conteúdo abaixo no arquivo, substituindo os valores pelos seus.

```env
# .env

# Chave de API para o Google Gemini
# Obrigatória para a geração de conteúdo. Obtenha em https://aistudio.google.com/
GEMINI_API_KEY="SUA_CHAVE_DE_API_AQUI"
```

**ALERTA:** A variável `GEMINI_API_KEY` é **obrigatória**. Sem ela, a funcionalidade de geração de conteúdo não funcionará.

## 4. Como Executar

Para iniciar o sistema em modo de linha de comando (CLI), execute o arquivo `main.py`.

```bash
python main.py
```

O sistema apresentará um menu interativo com as seguintes opções:
*   **Gerenciar Desafios (CRUD):** Permite criar, listar, atualizar e desativar desafios manualmente.
*   **Gerar Aula com IA:** Inicia o fluxo de geração de conteúdo com o Google Gemini.
*   **Exportar Dados JSON:** Permite exportar relatórios e dados do banco para arquivos `.json`.
*   **Testar Conexão:** Verifica se a conexão com o banco de dados Oracle está funcionando.
*   **Sair:** Encerra a aplicação.