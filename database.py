import oracledb
import json

def conectar_banco():
    try:
        # with open(r'C:\Users\paulo\Desktop\credenciais.json', 'r') as arquivo:
        #     file = json.load(arquivo)
        #     usr = file['login']
        #     psw = file['senha']

        conn = oracledb.connect(
            user='rm566358',
            password='fiap25',
            host='oracle.fiap.com.br',
            port=1521,
            sid='ORCL'
        )
        print("Conexão estabelecida com sucesso!")
        return conn

    except FileNotFoundError:
        print("Erro: Arquivo credenciais.json não encontrado!")
        return None
    except json.JSONDecodeError:
        print("Erro: Problema ao ler o arquivo JSON!")
        return None
    except oracledb.Error as e:
        print(f"Erro de conexão com o banco: {e}")
        return None


def testar_conexao():
    conn = conectar_banco()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "SELECT table_name FROM user_tables ORDER BY table_name"
                cursor.execute(sql)
                print("--- Tabelas deste usuário ---")
                resultado_query = cursor.fetchall()
                for linha in resultado_query:
                    print(linha[0])
        except oracledb.Error as e:
            print(f"Erro ao executar consulta: {e}")
        finally:
            conn.close()