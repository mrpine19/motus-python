from database import conectar_banco
import oracledb

def gerenciar_desafios():
    print("\n--- Gerenciar Desafios ---")
    print("1. Criar novo desafio")
    print("2. Listar desafios")
    print("3. Atualizar desafio")
    print("4. Excluir desafio")
    print("5. Voltar ao menu principal")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        criar_desafio()
    elif opcao == "2":
        listar_desafios()
    elif opcao == "3":
        atualizar_desafio()
    elif opcao == "4":
        excluir_desafio()
    elif opcao == "5":
        return
    else:
        print("Opção inválida!")


def criar_desafio():
    print("\n--- Criar Novo Desafio ---")

    conn = conectar_banco()
    if not conn:
        print("Erro: Não foi possível conectar ao banco de dados.")
        return

    try:
        with conn.cursor() as cursor:
            titulo = input("Título do desafio: ").strip()
            if not titulo:
                print("Título é obrigatório!")
                return

            descricao = input("Descrição do desafio: ").strip()
            if not descricao:
                print("Descrição é obrigatória!")
                return

            resposta_correta = input("Resposta correta: ").strip()
            if not resposta_correta:
                print("Resposta correta é obrigatória!")
                return

            feedback_explicacao = input("Feedback/explicação (opcional): ").strip()
            if not feedback_explicacao:
                feedback_explicacao = None

            ativo = input("Desafio ativo? (S/N) [padrão: S]: ").strip().upper()
            if not ativo or ativo not in ['S', 'N']:
                ativo = 'S'

            print("\n--- Níveis de Dificuldade ---")
            cursor.execute("""
                           SELECT id_nivel, codigo, descricao
                           FROM TB_MOT_NIVEL_COMPETENCIA
                           ORDER BY ordem
                           """)
            niveis = cursor.fetchall()

            if not niveis:
                print("Nenhum nível de competência cadastrado!")
                return

            for nivel in niveis:
                print(f"ID: {nivel[0]} - {nivel[1]} - {nivel[2]}")

            id_nivel_dificuldade = input("\nID do nível de dificuldade: ").strip()
            if not id_nivel_dificuldade.isdigit():
                print("ID do nível deve ser um número!")
                return

            print("\n--- Voluntários Disponíveis ---")
            cursor.execute("""
                           SELECT v.id_voluntario, u.nome
                           FROM TB_MOT_VOLUNTARIO v
                                    JOIN TB_MOT_USUARIO u ON v.id_usuario = u.id_usuario
                           WHERE u.ativo = 'S'
                           """)
            voluntarios = cursor.fetchall()

            if not voluntarios:
                print("Nenhum voluntário cadastrado!")
                return

            for voluntario in voluntarios:
                print(f"ID: {voluntario[0]} - Nome: {voluntario[1]}")

            id_voluntario_criador = input("\nID do voluntário criador: ").strip()
            if not id_voluntario_criador.isdigit():
                print("ID do voluntário deve ser um número!")
                return

            print("\n--- Áreas de Competência ---")
            cursor.execute("""
                           SELECT id_area, codigo, descricao
                           FROM TB_MOT_AREA_COMPETENCIA
                           ORDER BY codigo
                           """)
            areas = cursor.fetchall()

            if not areas:
                print("Nenhuma área de competência cadastrada!")
                return

            for area in areas:
                print(f"ID: {area[0]} - {area[1]} - {area[2]}")

            id_area_competencia = input("\nID da área de competência: ").strip()
            if not id_area_competencia.isdigit():
                print("ID da área deve ser um número!")
                return

            cursor.execute("SELECT SQ_MOT_DESAFIO.NEXTVAL FROM DUAL")
            id_desafio = cursor.fetchone()[0]

            sql_insert = """
                         INSERT INTO TB_MOT_DESAFIO (id_desafio, titulo, descricao, resposta_correta, \
                                                     feedback_explicacao, ativo, id_nivel_dificuldade, \
                                                     id_voluntario_criador, id_area_competencia) \
                         VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9) \
                         """

            cursor.execute(sql_insert, (
                id_desafio,
                titulo,
                descricao,
                resposta_correta,
                feedback_explicacao,
                ativo,
                int(id_nivel_dificuldade),
                int(id_voluntario_criador),
                int(id_area_competencia)
            ))

            conn.commit()
            print(f"Desafio criado com sucesso! ID: {id_desafio}")

    except oracledb.Error as e:
        conn.rollback()
        error_obj, = e.args
        if error_obj.code == 2291:
            print("Erro: ID inválido (nível, voluntário ou área não existe)")
        else:
            print(f"Erro ao criar desafio: {e}")
    except ValueError as e:
        conn.rollback()
        print(f"Erro de validação: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Erro inesperado: {e}")
    finally:
        conn.close()


def listar_desafios():
    print("\n--- Listar Desafios ---")
    conn = conectar_banco()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "SELECT id_desafio, titulo FROM TB_MOT_DESAFIO WHERE ativo = 'S'"
                cursor.execute(sql)
                desafios = cursor.fetchall()

                if desafios:
                    print("Desafios ativos:")
                    for desafio in desafios:
                        print(f"ID: {desafio[0]} - Título: {desafio[1]}")
                else:
                    print("Nenhum desafio encontrado.")
        except Exception as e:
            print(f"Erro ao listar desafios: {e}")
        finally:
            conn.close()


def atualizar_desafio():
    print("\n--- Atualizar Desafio ---")

    conn = conectar_banco()
    if not conn:
        print("Erro: Não foi possível conectar ao banco de dados.")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                           SELECT d.id_desafio,
                                  d.titulo,
                                  d.ativo,
                                  n.descricao as nivel,
                                  a.descricao as area
                           FROM TB_MOT_DESAFIO d
                                    JOIN TB_MOT_NIVEL_COMPETENCIA n ON d.id_nivel_dificuldade = n.id_nivel
                                    JOIN TB_MOT_AREA_COMPETENCIA a ON d.id_area_competencia = a.id_area
                           ORDER BY d.id_desafio
                           """)
            desafios = cursor.fetchall()

            if not desafios:
                print("Nenhum desafio cadastrado para atualizar!")
                return

            print("\n--- Desafios Disponíveis ---")
            for desafio in desafios:
                status = "Ativo" if desafio[2] == 'S' else "Inativo"
                print(f"ID: {desafio[0]} - {desafio[1]} ({status})")
                print(f"   Nível: {desafio[3]} | Área: {desafio[4]}\n")

            id_desafio = input("Digite o ID do desafio que deseja atualizar: ").strip()
            if not id_desafio.isdigit():
                print("ID do desafio deve ser um número!")
                return

            cursor.execute("""
                           SELECT id_desafio,
                                  titulo,
                                  descricao,
                                  resposta_correta,
                                  feedback_explicacao,
                                  ativo,
                                  id_nivel_dificuldade,
                                  id_voluntario_criador,
                                  id_area_competencia
                           FROM TB_MOT_DESAFIO
                           WHERE id_desafio = :1
                           """, (int(id_desafio),))

            desafio = cursor.fetchone()
            if not desafio:
                print("Desafio não encontrado!")
                return

            print(f"\nAtualizando desafio: {desafio[1]}")
            print("Deixe em branco para manter o valor atual.\n")

            titulo = input(f"Título [{desafio[1]}]: ").strip()
            titulo = titulo if titulo else desafio[1]

            descricao = input(f"Descrição [{desafio[2][:50]}...]: ").strip()
            descricao = descricao if descricao else desafio[2]

            resposta_correta = input(f"Resposta correta [{desafio[3]}]: ").strip()
            resposta_correta = resposta_correta if resposta_correta else desafio[3]

            feedback_atual = desafio[4] if desafio[4] else "(vazio)"
            feedback_explicacao = input(f"Feedback/explicação [{feedback_atual}]: ").strip()
            feedback_explicacao = feedback_explicacao if feedback_explicacao else desafio[4]

            ativo_atual = desafio[5]
            ativo = input(f"Ativo (S/N) [{ativo_atual}]: ").strip().upper()
            if ativo and ativo in ['S', 'N']:
                ativo = ativo
            else:
                ativo = ativo_atual

            cursor.execute("""
                           SELECT id_nivel, codigo, descricao
                           FROM TB_MOT_NIVEL_COMPETENCIA
                           ORDER BY ordem
                           """)
            niveis = cursor.fetchall()

            print("\n--- Níveis de Dificuldade ---")
            for nivel in niveis:
                print(f"ID: {nivel[0]} - {nivel[1]} - {nivel[2]}")

            nivel_atual = desafio[6]
            id_nivel_dificuldade = input(f"ID do nível de dificuldade [{nivel_atual}]: ").strip()
            if id_nivel_dificuldade and id_nivel_dificuldade.isdigit():
                id_nivel_dificuldade = int(id_nivel_dificuldade)
            else:
                id_nivel_dificuldade = nivel_atual

            cursor.execute("""
                           SELECT id_area, codigo, descricao
                           FROM TB_MOT_AREA_COMPETENCIA
                           ORDER BY codigo
                           """)
            areas = cursor.fetchall()

            print("\n--- Áreas de Competência ---")
            for area in areas:
                print(f"ID: {area[0]} - {area[1]} - {area[2]}")

            area_atual = desafio[8]
            id_area_competencia = input(f"ID da área de competência [{area_atual}]: ").strip()
            if id_area_competencia and id_area_competencia.isdigit():
                id_area_competencia = int(id_area_competencia)
            else:
                id_area_competencia = area_atual

            print(f"\n--- Resumo da Atualização ---")
            print(f"Título: {titulo}")
            print(f"Descrição: {descricao[:100]}...")
            print(f"Resposta correta: {resposta_correta}")
            print(f"Feedback: {feedback_explicacao[:50] if feedback_explicacao else '(vazio)'}")
            print(f"Ativo: {ativo}")
            print(f"Nível ID: {id_nivel_dificuldade}")
            print(f"Área ID: {id_area_competencia}")

            confirmar = input("\nConfirmar atualização? (S/N): ").strip().upper()
            if confirmar != 'S':
                print("Atualização cancelada!")
                return

            sql_update = """
                         UPDATE TB_MOT_DESAFIO
                         SET titulo = :1, 
                    descricao = :2, 
                    resposta_correta = :3, 
                    feedback_explicacao = :4, 
                    ativo = :5, 
                    id_nivel_dificuldade = :6, 
                    id_area_competencia = :7
                         WHERE id_desafio = :8 \
                         """

            cursor.execute(sql_update, (
                titulo,
                descricao,
                resposta_correta,
                feedback_explicacao,
                ativo,
                id_nivel_dificuldade,
                id_area_competencia,
                int(id_desafio)
            ))

            conn.commit()
            print(f"Desafio ID {id_desafio} atualizado com sucesso!")

    except oracledb.Error as e:
        conn.rollback()
        error_obj, = e.args
        if error_obj.code == 2291:
            print("Erro: ID inválido (nível ou área não existe)")
        else:
            print(f"Erro ao atualizar desafio: {e}")
    except ValueError as e:
        conn.rollback()
        print(f"Erro de validação: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Erro inesperado: {e}")
    finally:
        conn.close()


def excluir_desafio():
    print("\n--- Excluir Desafio ---")

    conn = conectar_banco()
    if not conn:
        print("Erro: Não foi possível conectar ao banco de dados.")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                           SELECT d.id_desafio, d.titulo, n.descricao as nivel, a.descricao as area
                           FROM TB_MOT_DESAFIO d
                                    JOIN TB_MOT_NIVEL_COMPETENCIA n ON d.id_nivel_dificuldade = n.id_nivel
                                    JOIN TB_MOT_AREA_COMPETENCIA a ON d.id_area_competencia = a.id_area
                           WHERE d.ativo = 'S'
                           ORDER BY d.id_desafio
                           """)
            desafios_ativos = cursor.fetchall()

            if not desafios_ativos:
                print("Nenhum desafio ativo encontrado para excluir!")
                return

            print("\n--- Desafios Ativos Disponíveis ---")
            for desafio in desafios_ativos:
                print(f"ID: {desafio[0]} - {desafio[1]}")
                print(f"   Nível: {desafio[2]} | Área: {desafio[3]}\n")

            id_desafio = input("Digite o ID do desafio que deseja excluir: ").strip()
            if not id_desafio.isdigit():
                print("ID do desafio deve ser um número!")
                return

            # Verificar se o desafio existe e está ativo
            cursor.execute("""
                           SELECT id_desafio, titulo, ativo
                           FROM TB_MOT_DESAFIO
                           WHERE id_desafio = :1
                           """, (int(id_desafio),))

            desafio = cursor.fetchone()
            if not desafio:
                print("Desafio não encontrado!")
                return

            if desafio[2] == 'N':
                print("Este desafio já está excluído (inativo)!")
                return

            cursor.execute("""
                           SELECT COUNT(*)
                           FROM TB_MOT_PONTUACAO
                           WHERE id_desafio = :1
                           """, (int(id_desafio),))

            count_pontuacoes = cursor.fetchone()[0]

            print(f"\nInformações do Desafio:")
            print(f"ID: {desafio[0]}")
            print(f"Título: {desafio[1]}")
            print(f"Status atual: Ativo")
            if count_pontuacoes > 0:
                print(f"⚠ ATENÇÃO: Este desafio possui {count_pontuacoes} pontuação(ões) registrada(s)")
                print("   Ao marcar como inativo, o histórico de pontuações será mantido.")

            print(f"\nEsta ação irá marcar o desafio como INATIVO.")
            print("O desafio não aparecerá mais para os alunos, mas permanecerá no banco.")

            confirmar = input("\n Confirmar exclusão? (Digite 'EXCLUIR' para confirmar): ").strip()
            if confirmar.upper() != 'EXCLUIR':
                print("Exclusão cancelada!")
                return

            sql_update = """
                         UPDATE TB_MOT_DESAFIO
                         SET ativo = 'N'
                         WHERE id_desafio = :1 \
                         """

            cursor.execute(sql_update, (int(id_desafio),))
            conn.commit()

            print(f"Desafio ID {id_desafio} excluído com sucesso (marcado como inativo)!")

    except oracledb.Error as e:
        conn.rollback()
        print(f"Erro ao excluir desafio: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Erro inesperado: {e}")
    finally:
        conn.close()