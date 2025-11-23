from google import genai
from dotenv import load_dotenv
import os
import json
import re
from database import conectar_banco
import oracledb

load_dotenv()

# --- Consultas SQL Auxiliares ---
CONSULTA_VOLUNTARIOS_ATIVOS = "SELECT id_voluntario, nome FROM TB_MOT_VOLUNTARIO v JOIN TB_MOT_USUARIO u ON v.id_usuario = u.id_usuario WHERE u.ativo = 'S' ORDER BY u.nome"
CONSULTA_AREAS_COMPETENCIA = "SELECT id_area, codigo, descricao FROM TB_MOT_AREA_COMPETENCIA ORDER BY codigo"

# --- Funções Auxiliares de UI ---
def _obter_input_numerico(prompt):
    """Solicita um número ao usuário e garante que a entrada seja um inteiro válido."""
    while True:
        valor_str = input(prompt).strip()
        if valor_str.isdigit():
            return int(valor_str)
        else:
            print("Entrada inválida. Por favor, digite um número inteiro.")

def _exibir_lista_opcoes(cursor, titulo, consulta_sql):
    """Executa uma consulta e exibe uma lista formatada de opções para o usuário."""
    print(f"\n--- {titulo} ---")
    try:
        cursor.execute(consulta_sql)
        items = cursor.fetchall()
        if not items:
            print(f"Nenhuma opção disponível em '{titulo}'.")
            return False
        
        for item in items:
            if len(item) >= 3:
                 print(f"ID: {item[0]} - {item[1]} - {item[2]}")
            else:
                 print(f"ID: {item[0]} - {item[1]}")
        return True
    except oracledb.DatabaseError as e:
        print(f"Erro ao buscar dados para '{titulo}': {e}")
        return False

class GeradorConteudoMotus:
    def __init__(self):
        """Inicializa o cliente da API Gemini"""
        try:
            self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
            self.model = "gemini-2.5-flash"
            print("Conectado à API Gemini")
        except Exception as e:
            print(f"Erro ao conectar com Gemini: {e}")
            self.client = None

    def criar_prompt_estruturado(self, tema):
        """Cria o prompt fusionado para geração de conteúdo"""
        prompt = f"""
Você é o Motus, um mentor educacional voluntário do projeto Vepinho, na zona sul de São Paulo.
Sua missão é explicar o tema: "{tema}" para jovens da Geração Z em situação de vulnerabilidade.

--- SUA PERSONALIDADE (TOM DE VOZ) ---
1.  **Mentor Parceiro:** Você fala de igual para igual, com empatia e incentivo. Use "nós", "bora", "se liga".
2.  **Gírias Leves:** Use linguagem natural, mas mantenha o respeito pedagógico.
3.  **Conexão Real:** Conecte TUDO ao cotidiano deles (futebol, música, jogos, corre). Nada de exemplos corporativos.
4.  **Antifragilidade:** Simplifique conceitos abstratos brutalmente.

--- CONTEXTO E DIRETRIZES CRÍTICAS ---
- Público: Jovens do 5º ao 9º ano, criativos, mas com recursos limitados e neurodiversidade (TDAH/Autismo).
- MISSÃO: Desenvolver competências do Futuro do Trabalho (Pensamento Analítico) para evitar exclusão tecnológica.

--- ESTRUTURA DE ENSINO (COMPETÊNCIAS WEF) ---
Gere 3 variações escalando a complexidade:

NÍVEL 1: BÁSICO -> Foco: LÓGICO-ANALÍTICO (Curiosidade)
- Explique o "O QUE É" usando analogia visual.
- Desafio: Identificação de padrões simples.

NÍVEL 2: MÉDIO -> Foco: CRIATIVO-ADAPTATIVO (Flexibilidade)
- Explique o "PARA QUE SERVE" na vida real ("treta" do dia a dia).
- Desafio: Solução de problemas práticos.

NÍVEL 3: AVANÇADO -> Foco: ESTRATÉGICO-COMPLEXO (Pensamento Analítico)
- Explique "COMO FUNCIONA A LÓGICA" por trás do sistema.
- Desafio: Tomada de decisão sob incerteza. Pensar "fora da caixa".

--- FORMATO DE SAÍDA (JSON ESTRITO PARA DDL) ---
Retorne APENAS um JSON válido com uma lista de 3 objetos.
IMPORTANTE: Como nosso banco de dados é rígido, você deve FORMATAR os campos de texto para incluir as dicas extras:

1. No campo 'material_explicativo', inicie com o TIPO DE HABILIDADE entre colchetes. Ex: "[Foco: Lógico-Analítico] Aqui vai a explicação..."
2. No campo 'feedback_explicacao', adicione a DICA DE NEURODIVERSIDADE ao final.

Siga este schema:
[
  {{
    "id_nivel_dificuldade": 1,
    "titulo": "Título curto estilo YouTube",
    "material_explicativo": "[Foco: Lógico-Analítico] Texto curto (max 400 chars) usando analogias. Tom: Mentor Parceiro.",
    "pergunta_interativa": "A pergunta do desafio.",
    "resposta_correta": "A resposta exata.",
    "feedback_explicacao": "Explicação do acerto. \\n💡 DICA MENTAL: Dica para alunos com TDAH (ex: desenhe no caderno)."
  }},
  {{
    "id_nivel_dificuldade": 2,
    "titulo": "Título focado em utilidade",
    "material_explicativo": "[Foco: Criativo-Adaptativo] Texto curto (max 400 chars) focado em aplicação prática.",
    "pergunta_interativa": "A pergunta do desafio.",
    "resposta_correta": "A resposta exata.",
    "feedback_explicacao": "Explicação da flexibilidade. \\n💡 DICA MENTAL: Dica de organização (ex: pense passo a passo)."
  }},
  {{
    "id_nivel_dificuldade": 3,
    "titulo": "Título Desafiador",
    "material_explicativo": "[Foco: Estratégico-Complexo] Texto curto (max 400 chars) focado em lógica pura.",
    "pergunta_interativa": "Pergunta difícil que exige Pensamento Analítico.",
    "resposta_correta": "A resposta exata.",
    "feedback_explicacao": "Explicação sistêmica. \\n💡 DICA MENTAL: Estratégia para sobrecarga (ex: respira e quebra o problema)."
  }}
]
"""
        return prompt

    def extrair_json_da_resposta(self, texto):
        """Extrai e valida o JSON da resposta da IA"""
        try:
            json_match = re.search(r'\[.*\]', texto, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                conteudo_gerado = json.loads(json_str)
                if (isinstance(conteudo_gerado, list) and
                        len(conteudo_gerado) > 0 and
                        all('id_nivel_dificuldade' in item for item in conteudo_gerado)):
                    return conteudo_gerado
                else:
                    print("Estrutura JSON inválida (não é uma lista ou itens não contêm 'id_nivel_dificuldade')")
                    return None
            else:
                print("Nenhum JSON encontrado na resposta")
                return None
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao extrair JSON: {e}")
            return None

    def gerar_conteudo_educacional(self, tema):
        """Gera conteúdo educacional usando Gemini API"""
        if not self.client:
            print("Cliente Gemini não inicializado")
            return None
        print(f"Gerando conteúdo sobre: {tema}")
        print("Consultando IA...")
        try:
            prompt = self.criar_prompt_estruturado(tema)
            response = self.client.models.generate_content(model=self.model, contents=prompt)
            conteudo_gerado = self.extrair_json_da_resposta(response.text)
            if conteudo_gerado:
                print("Conteúdo gerado com sucesso!")
                return conteudo_gerado
            else:
                print("Falha ao gerar conteúdo válido")
                return None
        except Exception as e:
            print(f"Erro na API Gemini: {e}")
            return None

    def salvar_conteudo_no_banco(self, conteudo_gerado, tema, id_voluntario, id_area):
        """Salva o conteúdo gerado no banco de dados, recebendo os IDs como parâmetros."""
        conn = conectar_banco()
        if not conn:
            print("Erro ao conectar no banco!")
            return False
        try:
            with conn.cursor() as cursor:
                desafios_criados = 0
                for exercicio in conteudo_gerado:
                    cursor.execute("SELECT SQ_MOT_DESAFIO.NEXTVAL FROM DUAL")
                    id_desafio = cursor.fetchone()[0]
                    sql_inserir = """
                                  INSERT INTO TB_MOT_DESAFIO (id_desafio, titulo, descricao, resposta_correta,
                                                              feedback_explicacao, ativo, id_nivel_dificuldade,
                                                              id_voluntario_criador, id_area_competencia)
                                  VALUES (:1, :2, :3, :4, :5, 'S', :6, :7, :8)
                                  """
                    descricao_completa = (
                        f"{exercicio.get('material_explicativo', '')}\n\n"
                        f"PERGUNTA: {exercicio.get('pergunta_interativa', '')}"
                    )
                    cursor.execute(sql_inserir, (
                        id_desafio,
                        exercicio.get('titulo', f'Desafio sobre {tema}'),
                        descricao_completa,
                        exercicio.get('resposta_correta', ''),
                        exercicio.get('feedback_explicacao', ''),
                        exercicio.get('id_nivel_dificuldade', 1),
                        id_voluntario,
                        id_area
                    ))
                    desafios_criados += 1
                    print(f"Desafio Nível {exercicio.get('id_nivel_dificuldade')} salvo (ID: {id_desafio})")
                conn.commit()
                print(f"🎉 Total de {desafios_criados} desafios salvos no banco!")
                return True
        except Exception as e:
            print(f"Erro ao salvar no banco: {e}")
            conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

def gerar_aula_ia():
    """Função principal para gerar aulas com IA - chamada pelo menu"""
    print("\n" + "=" * 60)
    print("MOTUS.IA - GERADOR DE CONTEÚDO ADAPTATIVO")
    print("=" * 60)
    tema = input("\nDigite o tema da aula: ").strip()
    if not tema:
        print("Tema é obrigatório!")
        return
    gerador = GeradorConteudoMotus()
    if not gerador.client:
        return
    conteudo_gerado = gerador.gerar_conteudo_educacional(tema)
    if conteudo_gerado:
        print("\nPRÉVIA DO CONTEÚDO GERADO:")
        print("-" * 40)
        for exercicio in conteudo_gerado:
            print(f"\nNível {exercicio.get('id_nivel_dificuldade')}")
            print(f"Título: {exercicio.get('titulo', 'N/A')}")
            print(f"Pergunta: {exercicio.get('pergunta_interativa', 'N/A')[:80]}...")
        
        salvar = input("\nDeseja salvar esses desafios no banco? (S/N): ").strip().upper()
        if salvar == 'S':
            conn = conectar_banco()
            if not conn:
                print("Não foi possível conectar ao banco para obter opções.")
                return
            try:
                with conn.cursor() as cursor:
                    if not _exibir_lista_opcoes(cursor, "Voluntário Criador", CONSULTA_VOLUNTARIOS_ATIVOS):
                        return
                    id_voluntario = _obter_input_numerico("Digite o ID do voluntário criador: ")

                    if not _exibir_lista_opcoes(cursor, "Área de Competência", CONSULTA_AREAS_COMPETENCIA):
                        return
                    id_area = _obter_input_numerico("Digite o ID da área de competência: ")
            finally:
                if conn:
                    conn.close()

            if gerador.salvar_conteudo_no_banco(conteudo_gerado, tema, id_voluntario, id_area):
                print("Conteúdo salvo com sucesso!")
            else:
                print("Erro ao salvar conteúdo")
        else:
            print("Conteúdo não salvo (apenas visualização)")

        exportar = input("\nDeseja exportar para JSON? (S/N): ").strip().upper()
        if exportar == 'S':
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"conteudo_gerado_{tema.replace(' ', '_')}_{timestamp}.json"
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(conteudo_gerado, f, ensure_ascii=False, indent=2)
            print(f"Conteúdo exportado: {nome_arquivo}")
    else:
        print("Não foi possível gerar conteúdo para este tema")

def teste_rapido():
    """Função para testar a geração de conteúdo"""
    print("TESTE RÁPIDO DO GERADOR")
    tema_teste = "Porcentagem no dia a dia"
    gerador = GeradorConteudoMotus()
    if not gerador.client:
        print("Teste falhou: Cliente não inicializado.")
        return
    conteudo = gerador.gerar_conteudo_educacional(tema_teste)
    if conteudo:
        print("Teste bem-sucedido!")
        for item in conteudo:
            print(f"\n--- Nível {item.get('id_nivel_dificuldade')} ---")
            print(f"Título: {item.get('titulo')}")
            print(f"Pergunta: {item.get('pergunta_interativa')}")
    else:
        print("Teste falhou")

if __name__ == "__main__":
    teste_rapido()