from database import conectar_banco, testar_conexao
from crud_desafios import gerenciar_desafios
from consultas_json import exportar_dados_json
from ia_educacao import gerar_aula_ia


def mostrar_menu():
    print("\n" + "=" * 50)
    print("        SISTEMA DE EDUCAÇÃO ADAPTATIVA")
    print("=" * 50)
    print("1. Gerenciar Desafios (CRUD)")
    print("2. Gerar Aula com IA")
    print("3. Exportar Dados JSON")
    print("4. Testar Conexão com Banco")
    print("0. Sair")
    print("=" * 50)


def validar_opcao(opcao):
    try:
        opcao_int = int(opcao)
        if 0 <= opcao_int <= 4:
            return True
        else:
            return False
    except ValueError:
        return False


def main():
    print("Bem-vindo ao Sistema de Educação Adaptativa!")

    while True:
        mostrar_menu()
        opcao = input("Digite sua opção: ")

        if not validar_opcao(opcao):
            print("Opção inválida! Digite um número entre 0 e 4.")
            continue

        opcao = int(opcao)

        if opcao == 0:
            print("👋 Obrigado por usar o sistema! Até logo!")
            break
        elif opcao == 1:
            gerenciar_desafios()
        elif opcao == 2:
            gerar_aula_ia()
        elif opcao == 3:
            exportar_dados_json()
        elif opcao == 4:
            testar_conexao()


if __name__ == "__main__":
    main()