from database import conectar_banco
import oracledb

# --- Consultas SQL Globais ---
CONSULTA_NIVEL_DIFICULDADE = "SELECT id_nivel, codigo, descricao FROM TB_MOT_NIVEL_COMPETENCIA ORDER BY ordem"
CONSULTA_VOLUNTARIOS_ATIVOS = "SELECT id_voluntario, nome FROM TB_MOT_VOLUNTARIO v JOIN TB_MOT_USUARIO u ON v.id_usuario = u.id_usuario WHERE u.ativo = 'S'"
CONSULTA_AREAS_COMPETENCIA = "SELECT id_area, codigo, descricao FROM TB_MOT_AREA_COMPETENCIA ORDER BY codigo"
CONSULTA_PROXIMO_ID_DESAFIO = "SELECT SQ_MOT_DESAFIO.NEXTVAL FROM DUAL"
INSERIR_DESAFIO = """
    INSERT INTO TB_MOT_DESAFIO (
        id_desafio, titulo, descricao, resposta_correta, feedback_explicacao,
        ativo, id_nivel_dificuldade, id_voluntario_criador, id_area_competencia
    ) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
"""
CONSULTA_DESAFIOS_ATIVOS = "SELECT id_desafio, titulo FROM TB_MOT_DESAFIO WHERE ativo = 'S'"
CONSULTA_TODOS_DESAFIOS_DETALHADO = """
    SELECT d.id_desafio, d.titulo, d.ativo, n.descricao as nivel, a.descricao as area
    FROM TB_MOT_DESAFIO d
    JOIN TB_MOT_NIVEL_COMPETENCIA n ON d.id_nivel_dificuldade = n.id_nivel
    JOIN TB_MOT_AREA_COMPETENCIA a ON d.id_area_competencia = a.id_area
    ORDER BY d.id_desafio
"""
CONSULTA_DESAFIO_POR_ID = """
    SELECT id_desafio, titulo, descricao, resposta_correta, feedback_explicacao,
           ativo, id_nivel_dificuldade, id_voluntario_criador, id_area_competencia
    FROM TB_MOT_DESAFIO
    WHERE id_desafio = :1
"""
ATUALIZAR_DESAFIO = """
    UPDATE TB_MOT_DESAFIO
    SET titulo = :1, descricao = :2, resposta_correta = :3, feedback_explicacao = :4,
        ativo = :5, id_nivel_dificuldade = :6, id_area_competencia = :7
    WHERE id_desafio = :8
"""
CONSULTA_DESAFIOS_ATIVOS_DETALHADO = """
    SELECT d.id_desafio, d.titulo, n.descricao as nivel, a.descricao as area
    FROM TB_MOT_DESAFIO d
    JOIN TB_MOT_NIVEL_COMPETENCIA n ON d.id_nivel_dificuldade = n.id_nivel
    JOIN TB_MOT_AREA_COMPETENCIA a ON d.id_area_competencia = a.id_area
    WHERE d.ativo = 'S'
    ORDER BY d.id_desafio
"""
CONSULTA_DESAFIO_SIMPLES_POR_ID = "SELECT id_desafio, titulo, ativo FROM TB_MOT_DESAFIO WHERE id_desafio = :1"
CONTAR_PONTUACOES_POR_DESAFIO = "SELECT COUNT(*) as total FROM TB_MOT_PONTUACAO WHERE id_desafio = :1"
DESATIVAR_DESAFIO = "UPDATE TB_MOT_DESAFIO SET ativo = 'N' WHERE id_desafio = :1"

# --- Funções Auxiliares ---

def _obter_input_obrigatorio(prompt):
    """Solicita uma entrada ao usuário e garante que não seja vazia."""
    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        else:
            print("Entrada inválida. Este campo é obrigatório.")

def _obter_input_numerico(prompt):
    """Solicita um número ao usuário e garante que a entrada seja um inteiro válido."""
    while True:
        valor_str = input(prompt).strip()
        if valor_str.isdigit():
            return int(valor_str)
        else:
            print("Entrada inválida. Por favor, digite um número inteiro.")

def _obter_input_opcional(prompt, valor_atual):
    """Solicita uma entrada opcional, retornando o valor atual se nada for digitado."""
    valor = input(prompt).strip()
    return valor if valor else valor_atual

def _row_to_dict(cursor, row):
    """Converte uma única linha (tupla) do banco em um dicionário."""
    if not row:
        return None
    col_names = [d[0].lower() for d in cursor.description]
    return dict(zip(col_names, row))

def _exibir_lista_opcoes(cursor, titulo, consulta_sql, parametros=None):
    """Executa uma consulta e exibe uma lista formatada, acessando colunas por índice."""
    print(f"\n--- {titulo} ---")
    try:
        cursor.execute(consulta_sql, parametros or [])
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

# --- Funções de Gerenciamento ---

def gerenciar_desafios():
    """Exibe o menu de gerenciamento de desafios."""
    while True:
        print("\n--- Gerenciar Desafios ---")
        print("1. Criar novo desafio")
        print("2. Listar desafios")
        print("3. Atualizar desafio")
        print("4. Excluir desafio (inativar)")
        print("5. Voltar ao menu principal")
        opcao = input("Escolha uma opção: ")
        if opcao == "1": criar_desafio()
        elif opcao == "2": listar_desafios()
        elif opcao == "3": atualizar_desafio()
        elif opcao == "4": excluir_desafio()
        elif opcao == "5": break
        else: print("Opção inválida! Tente novamente.")


def criar_desafio():
    """Orquestra a criação de um novo desafio."""
    print("\n--- Criar Novo Desafio ---")
    conn = conectar_banco()
    if not conn: return

    try:
        with conn.cursor() as cursor:
            titulo = _obter_input_obrigatorio("Título do desafio: ")
            descricao = _obter_input_obrigatorio("Descrição do desafio: ")
            resposta_correta = _obter_input_obrigatorio("Resposta correta: ")
            
            feedback_explicacao = input("Feedback/explicação (opcional): ").strip() or None
            ativo = input("Desafio ativo? (S/N) [padrão: S]: ").strip().upper()
            ativo = ativo if ativo in ['S', 'N'] else 'S'

            if not _exibir_lista_opcoes(cursor, "Níveis de Dificuldade", CONSULTA_NIVEL_DIFICULDADE): return
            id_nivel = _obter_input_numerico("\nID do nível de dificuldade: ")

            if not _exibir_lista_opcoes(cursor, "Voluntários Disponíveis", CONSULTA_VOLUNTARIOS_ATIVOS): return
            id_voluntario = _obter_input_numerico("\nID do voluntário criador: ")

            if not _exibir_lista_opcoes(cursor, "Áreas de Competência", CONSULTA_AREAS_COMPETENCIA): return
            id_area = _obter_input_numerico("\nID da área de competência: ")

            cursor.execute(CONSULTA_PROXIMO_ID_DESAFIO)
            id_desafio = cursor.fetchone()[0]

            cursor.execute(INSERIR_DESAFIO, (
                id_desafio, titulo, descricao, resposta_correta, feedback_explicacao, ativo,
                id_nivel, id_voluntario, id_area
            ))
            conn.commit()
            print(f"Desafio criado com sucesso! ID: {id_desafio}")

    except oracledb.DatabaseError as e:
        conn.rollback()
        error, = e.args
        if error.code == 2291: print("Erro: Um dos IDs (nível, voluntário ou área) é inválido.")
        else: print(f"Erro de banco de dados: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Erro inesperado: {e}")
    finally:
        if conn: conn.close()


def listar_desafios():
    """Lista todos os desafios ativos no banco de dados."""
    print("\n--- Listar Desafios Ativos ---")
    conn = conectar_banco()
    if not conn: return

    try:
        with conn.cursor() as cursor:
            if not _exibir_lista_opcoes(cursor, "Desafios Ativos", CONSULTA_DESAFIOS_ATIVOS):
                print("Nenhum desafio ativo encontrado.")
    except oracledb.DatabaseError as e:
        print(f"Erro de banco de dados: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        if conn: conn.close()


def atualizar_desafio():
    """Orquestra a atualização de um desafio existente."""
    print("\n--- Atualizar Desafio ---")
    conn = conectar_banco()
    if not conn: return

    try:
        with conn.cursor() as cursor:
            cursor.execute(CONSULTA_TODOS_DESAFIOS_DETALHADO)
            rows = cursor.fetchall()
            if not rows:
                print("Nenhum desafio cadastrado para atualizar!")
                return

            col_names = [d[0].lower() for d in cursor.description]
            desafios = [dict(zip(col_names, row)) for row in rows]

            print("\n--- Desafios Disponíveis ---")
            for d in desafios:
                status = "Ativo" if d['ativo'] == 'S' else "Inativo"
                print(f"ID: {d['id_desafio']} - {d['titulo']} ({status})\n   Nível: {d['nivel']} | Área: {d['area']}\n")

            id_desafio = _obter_input_numerico("Digite o ID do desafio que deseja atualizar: ")

            cursor.execute(CONSULTA_DESAFIO_POR_ID, (id_desafio,))
            desafio_atual = _row_to_dict(cursor, cursor.fetchone())
            if not desafio_atual:
                print("Desafio não encontrado!")
                return

            print(f"\nAtualizando desafio: {desafio_atual['titulo']}")
            print("Deixe em branco para manter o valor atual.\n")

            titulo = _obter_input_opcional(f"Título [{desafio_atual['titulo']}]: ", desafio_atual['titulo'])
            descricao = _obter_input_opcional(f"Descrição [{desafio_atual['descricao'][:50]}...]: ", desafio_atual['descricao'])
            resposta = _obter_input_opcional(f"Resposta [{desafio_atual['resposta_correta']}]: ", desafio_atual['resposta_correta'])
            feedback = _obter_input_opcional(f"Feedback [{desafio_atual['feedback_explicacao'] or '(vazio)'}]: ", desafio_atual['feedback_explicacao'])
            ativo = _obter_input_opcional(f"Ativo (S/N) [{desafio_atual['ativo']}]: ", desafio_atual['ativo']).upper()

            if not _exibir_lista_opcoes(cursor, "Níveis de Dificuldade", CONSULTA_NIVEL_DIFICULDADE): return
            id_nivel = _obter_input_opcional(f"ID do nível [{desafio_atual['id_nivel_dificuldade']}]: ", desafio_atual['id_nivel_dificuldade'])

            if not _exibir_lista_opcoes(cursor, "Áreas de Competência", CONSULTA_AREAS_COMPETENCIA): return
            id_area = _obter_input_opcional(f"ID da área [{desafio_atual['id_area_competencia']}]: ", desafio_atual['id_area_competencia'])

            confirmar = input("\nConfirmar atualização? (S/N): ").strip().upper()
            if confirmar != 'S':
                print("Atualização cancelada.")
                return

            cursor.execute(ATUALIZAR_DESAFIO, (
                titulo, descricao, resposta, feedback, ativo,
                int(id_nivel), int(id_area), id_desafio
            ))
            conn.commit()
            print(f"Desafio ID {id_desafio} atualizado com sucesso!")

    except oracledb.DatabaseError as e:
        conn.rollback()
        error, = e.args
        if error.code == 2291: print("Erro: ID de nível ou área inválido.")
        else: print(f"Erro de banco de dados: {e}")
    except (ValueError, TypeError):
        conn.rollback()
        print("Erro de validação: Verifique se os IDs são números inteiros.")
    except Exception as e:
        conn.rollback()
        print(f"Erro inesperado: {e}")
    finally:
        if conn: conn.close()


def excluir_desafio():
    """Orquestra a exclusão lógica (inativação) de um desafio."""
    print("\n--- Excluir (Inativar) Desafio ---")
    conn = conectar_banco()
    if not conn: return

    try:
        with conn.cursor() as cursor:
            if not _exibir_lista_opcoes(cursor, "Desafios Ativos Disponíveis", CONSULTA_DESAFIOS_ATIVOS_DETALHADO):
                print("Nenhum desafio ativo encontrado para excluir!")
                return

            id_desafio = _obter_input_numerico("\nDigite o ID do desafio que deseja excluir: ")

            cursor.execute(CONSULTA_DESAFIO_SIMPLES_POR_ID, (id_desafio,))
            desafio = _row_to_dict(cursor, cursor.fetchone())
            if not desafio:
                print("Desafio não encontrado!")
                return
            if desafio['ativo'] == 'N':
                print("Este desafio já está inativo!")
                return

            cursor.execute(CONTAR_PONTUACOES_POR_DESAFIO, (id_desafio,))
            count_pontuacoes = cursor.fetchone()[0]

            print(f"\nInformações do Desafio: ID: {desafio['id_desafio']}, Título: {desafio['titulo']}")
            if count_pontuacoes > 0:
                print(f"Atenção: Este desafio possui {count_pontuacoes} pontuação(ões) registrada(s).")
            
            confirmar = input("\nDigite 'EXCLUIR' para confirmar a inativação: ").strip().upper()
            if confirmar != 'EXCLUIR':
                print("Exclusão cancelada.")
                return

            cursor.execute(DESATIVAR_DESAFIO, (id_desafio,))
            conn.commit()
            print(f"Desafio ID {id_desafio} foi inativado com sucesso!")

    except oracledb.DatabaseError as e:
        conn.rollback()
        print(f"Erro de banco de dados ao excluir desafio: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Erro inesperado ao excluir desafio: {e}")
    finally:
        if conn: conn.close()