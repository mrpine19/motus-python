from database import conectar_banco
import json


def exportar_dados_json():
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
        print("❌ Opção inválida!")


def exportar_desafios_nivel():
    print("Exportando desafios por nível...")


def exportar_progresso_alunos():
    print("Exportando progresso dos alunos...")


def exportar_estatisticas_desafios():
    print("Exportando estatísticas...")