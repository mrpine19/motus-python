import oracledb
import json
from datetime import datetime
from database import conectar_banco

# --- Consultas SQL Globais ---

CONSULTA_DESAFIOS_POR_NIVEL = """
      SELECT nc.id_nivel,
             nc.codigo                                      as nivel_codigo,
             nc.descricao                                   as nivel_descricao,
             nc.ordem                                       as nivel_ordem,
             COUNT(d.id_desafio)                            as total_desafios,
             SUM(CASE WHEN d.ativo = 'S' THEN 1 ELSE 0 END) as desafios_ativos,
             SUM(CASE WHEN d.ativo = 'N' THEN 1 ELSE 0 END) as desafios_inativos,
             LISTAGG(d.id_desafio || ':' || d.titulo, '; ')
                WITHIN GROUP (ORDER BY d.id_desafio) as desafios_lista
      FROM TB_MOT_NIVEL_COMPETENCIA nc
          LEFT JOIN TB_MOT_DESAFIO d
      ON nc.id_nivel = d.id_nivel_dificuldade
      GROUP BY nc.id_nivel, nc.codigo, nc.descricao, nc.ordem
      ORDER BY nc.ordem
      """

CONSULTA_PROGRESSO_ALUNOS = """
      SELECT u.nome                                         as nome_aluno,
             t.nome                                         as turma,
             nc.codigo                                      as nivel_atual,
             a.streak_atual,
             COUNT(p.id_pontuacao)                          as total_desafios,
             SUM(CASE WHEN p.acertou = 1 THEN 1 ELSE 0 END) as desafios_acertados,
             SUM(p.pontos)                                  as total_pontos
      FROM TB_MOT_ALUNO a
               JOIN TB_MOT_USUARIO u ON a.id_usuario = u.id_usuario
               JOIN TB_MOT_TURMA t ON a.id_turma = t.id_turma
               LEFT JOIN TB_MOT_NIVEL_COMPETENCIA nc ON a.id_nivel_atual = nc.id_nivel
               LEFT JOIN TB_MOT_PONTUACAO p ON a.id_aluno = p.id_aluno
      WHERE u.ativo = 'S'
      GROUP BY u.nome, t.nome, nc.codigo, a.streak_atual
      ORDER BY t.nome, u.nome
      """

CONSULTA_ESTATISTICAS_GERAIS_DESAFIOS = """
      SELECT COUNT(*)                                     as total_desafios,
             SUM(CASE WHEN ativo = 'S' THEN 1 ELSE 0 END) as desafios_ativos,
             SUM(CASE WHEN ativo = 'N' THEN 1 ELSE 0 END) as desafios_inativos,
             COUNT(DISTINCT id_area_competencia)          as areas_diferentes,
             COUNT(DISTINCT id_nivel_dificuldade)         as niveis_diferentes
      FROM TB_MOT_DESAFIO
      """

CONSULTA_DESAFIOS_AGRUPADOS_POR_NIVEL = """
     SELECT nc.codigo, COUNT(d.id_desafio) as total
     FROM TB_MOT_NIVEL_COMPETENCIA nc
              LEFT JOIN TB_MOT_DESAFIO d ON nc.id_nivel = d.id_nivel_dificuldade
     GROUP BY nc.codigo, nc.ordem
     ORDER BY nc.ordem
     """

CONSULTA_DESAFIOS_AGRUPADOS_POR_AREA = """
    SELECT ac.codigo, COUNT(d.id_desafio) as total
    FROM TB_MOT_AREA_COMPETENCIA ac
             LEFT JOIN TB_MOT_DESAFIO d ON ac.id_area = d.id_area_competencia
    GROUP BY ac.codigo
    ORDER BY ac.codigo
    """


def exportar_dados_json():
    """Menu para exportação de dados em formato JSON."""
    print("\n--- Exportar Dados JSON ---")
    print("1. Exportar desafios por nível")
    print("2. Exportar progresso dos alunos")
    print("3. Exportar estatísticas de desafios")
    print("4. Voltar")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        exportar_desafios_nivel()
    elif opcao == "2":
        exportar_progresso_alunos()
    elif opcao == "3":
        exportar_estatisticas_desafios()
    elif opcao == "4":
        return
    else:
        print("Opção inválida!")


def exportar_desafios_nivel():
    """Exporta desafios agrupados por nível de dificuldade para um arquivo JSON."""
    print("\n--- Exportar Desafios por Nível ---")
    conn = conectar_banco()
    if not conn:
        print("Erro: Não foi possível conectar ao banco de dados.")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute(CONSULTA_DESAFIOS_POR_NIVEL)
            resultados = cursor.fetchall()

            if not resultados:
                print("Nenhum dado encontrado para exportar!")
                return

            dados_exportacao = {
                "metadata": {
                    "exportacao_tipo": "desafios_por_nivel",
                    "data_exportacao": datetime.now().isoformat(),
                    "total_niveis": len(resultados),
                    "sistema": "Sistema de Educação Adaptativa"
                },
                "niveis": []
            }
            total_desafios_geral = 0
            total_ativos_geral = 0

            for linha in resultados:
                id_nivel, nivel_codigo, nivel_descricao, nivel_ordem, total_desafios, ativos, inativos, desafios_lista = linha
                desafios_detalhados = []
                if desafios_lista:
                    for desafio_info in desafios_lista.split('; '):
                        if ':' in desafio_info:
                            desafio_id, desafio_titulo = desafio_info.split(':', 1)
                            desafios_detalhados.append({"id": int(desafio_id), "titulo": desafio_titulo.strip()})

                nivel_data = {
                    "id_nivel": id_nivel,
                    "codigo": nivel_codigo,
                    "descricao": nivel_descricao,
                    "ordem": nivel_ordem,
                    "estatisticas": {
                        "total_desafios": total_desafios or 0,
                        "desafios_ativos": ativos or 0,
                        "desafios_inativos": inativos or 0,
                        "taxa_ativos": round((ativos / total_desafios * 100), 2) if total_desafios and total_desafios > 0 else 0
                    },
                    "desafios": desafios_detalhados
                }
                dados_exportacao["niveis"].append(nivel_data)
                total_desafios_geral += (total_desafios or 0)
                total_ativos_geral += (ativos or 0)

            dados_exportacao["metadata"]["total_desafios"] = total_desafios_geral
            dados_exportacao["metadata"]["total_ativos"] = total_ativos_geral
            dados_exportacao["metadata"]["taxa_ativos_geral"] = round((total_ativos_geral / total_desafios_geral * 100), 2) if total_desafios_geral > 0 else 0

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"desafios_por_nivel_{timestamp}.json"

            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo_json:
                json.dump(dados_exportacao, arquivo_json, ensure_ascii=False, indent=2)

            print(f"Sucesso: Dados exportados para o arquivo: {nome_arquivo}")
            print("\nResumo da Exportação:")
            print(f"   - Níveis de competência: {len(resultados)}")
            print(f"   - Total de desafios: {total_desafios_geral}")
            print(f"   - Desafios ativos: {total_ativos_geral}")
            print(f"   - Taxa de ativos: {dados_exportacao['metadata']['taxa_ativos_geral']}%")
            print("\nDetalhes por Nível:")
            for nivel in dados_exportacao["niveis"]:
                stats = nivel["estatisticas"]
                print(f"   - {nivel['codigo']} ({nivel['descricao']}): {stats['desafios_ativos']} ativos / {stats['total_desafios']} total")

    except oracledb.Error as e:
        print(f"Erro ao executar consulta no banco: {e}")
    except Exception as e:
        print(f"Erro durante exportação: {e}")
    finally:
        if conn:
            conn.close()


def exportar_progresso_alunos():
    """Exporta o progresso dos alunos para um arquivo JSON."""
    print("\n--- Exportar Progresso dos Alunos ---")
    conn = conectar_banco()
    if not conn:
        print("Erro: Não foi possível conectar ao banco de dados.")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute(CONSULTA_PROGRESSO_ALUNOS)
            resultados = cursor.fetchall()

            if not resultados:
                print("Nenhum aluno encontrado!")
                return

            dados_exportacao = {
                "exportado_em": datetime.now().isoformat(),
                "total_alunos": len(resultados),
                "alunos": []
            }

            for linha in resultados:
                nome, turma, nivel, streak, total_desafios, acertos, pontos = linha
                taxa_acerto = round((acertos / total_desafios) * 100, 1) if total_desafios and total_desafios > 0 else 0

                aluno_data = {
                    "nome": nome,
                    "turma": turma,
                    "nivel_atual": nivel or "Não definido",
                    "streak": streak or 0,
                    "desempenho": {
                        "total_desafios": total_desafios or 0,
                        "desafios_acertados": acertos or 0,
                        "taxa_acerto": taxa_acerto,
                        "pontos_totais": pontos or 0
                    }
                }
                dados_exportacao["alunos"].append(aluno_data)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"progresso_alunos_{timestamp}.json"

            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo_json:
                json.dump(dados_exportacao, arquivo_json, ensure_ascii=False, indent=2)

            print(f"Sucesso: Exportado para o arquivo: {nome_arquivo}")
            print(f"Alunos exportados: {len(resultados)}")
            if resultados:
                primeiro = dados_exportacao["alunos"][0]
                print(f"Exemplo: {primeiro['nome']} - {primeiro['desempenho']['taxa_acerto']}% de acerto")

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if conn:
            conn.close()


def exportar_estatisticas_desafios():
    """Exporta estatísticas gerais dos desafios para um arquivo JSON."""
    print("\n--- Exportar Estatísticas dos Desafios ---")
    conn = conectar_banco()
    if not conn:
        print("Erro: Não foi possível conectar ao banco de dados.")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute(CONSULTA_ESTATISTICAS_GERAIS_DESAFIOS)
            stats_gerais = cursor.fetchone()

            cursor.execute(CONSULTA_DESAFIOS_AGRUPADOS_POR_NIVEL)
            por_nivel = cursor.fetchall()

            cursor.execute(CONSULTA_DESAFIOS_AGRUPADOS_POR_AREA)
            por_area = cursor.fetchall()

            dados_exportacao = {
                "exportado_em": datetime.now().isoformat(),
                "estatisticas_gerais": {
                    "total_desafios": stats_gerais[0],
                    "desafios_ativos": stats_gerais[1],
                    "desafios_inativos": stats_gerais[2],
                    "areas_diferentes": stats_gerais[3],
                    "niveis_diferentes": stats_gerais[4]
                },
                "desafios_por_nivel": [{"nivel": nivel, "total": total} for nivel, total in por_nivel],
                "desafios_por_area": [{"area": area, "total": total} for area, total in por_area]
            }

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"estatisticas_desafios_{timestamp}.json"

            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo_json:
                json.dump(dados_exportacao, arquivo_json, ensure_ascii=False, indent=2)

            print(f"Sucesso: Exportado para o arquivo: {nome_arquivo}")
            print(f"Total de desafios: {stats_gerais[0]}")
            print(f"Ativos: {stats_gerais[1]} | Inativos: {stats_gerais[2]}")
            print(f"Níveis: {stats_gerais[4]} | Áreas: {stats_gerais[3]}")

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if conn:
            conn.close()