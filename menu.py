clientes = []
produtos = []

def cadastrar_cliente():
    print("\nCadastro de Cliente")
    nome = input("Nome: ").strip()
    telefone = input("Telefone: ").strip()
    if nome:
        clientes.append({"nome": nome, "telefone": telefone})
        print("Cliente cadastrado com sucesso.")
    else:
        print("Nome obrigatório. Cadastro cancelado.")

def listar_clientes():
    print("\nLista de Clientes")
    if not clientes:
        print("Nenhum cliente cadastrado.")
        return
    for i, cliente in enumerate(clientes, start=1):
        print(f"{i}. {cliente['nome']} - {cliente['telefone']}")

def submenu_clientes():
    while True:
        print("\n--- Gerenciar Clientes ---")
        print("1. Cadastrar cliente")
        print("2. Listar clientes")
        print("3. Voltar")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            cadastrar_cliente()
        elif opcao == "2":
            listar_clientes()
        elif opcao == "3":
            break
        else:
            print("Opção inválida. Tente novamente.")

def cadastrar_produto():
    print("\nCadastro de Produto")
    nome = input("Nome do produto: ").strip()
    preco = input("Preço: ").strip()
    if nome:
        produtos.append({"nome": nome, "preco": preco})
        print("Produto cadastrado com sucesso.")
    else:
        print("Nome obrigatório. Cadastro cancelado.")

def listar_produtos():
    print("\nLista de Produtos")
    if not produtos:
        print("Nenhum produto cadastrado.")
        return
    for i, produto in enumerate(produtos, start=1):
        print(f"{i}. {produto['nome']} - {produto['preco']}")

def submenu_produtos():
    while True:
        print("\n--- Gerenciar Produtos ---")
        print("1. Cadastrar produto")
        print("2. Listar produtos")
        print("3. Voltar")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            cadastrar_produto()
        elif opcao == "2":
            listar_produtos()
        elif opcao == "3":
            break
        else:
            print("Opção inválida. Tente novamente.")

def menu_principal():
    while True:
        print("\n=== Menu Principal ===")
        print("1. Gerenciar clientes")
        print("2. Gerenciar produtos")
        print("3. Sair")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            submenu_clientes()
        elif opcao == "2":
            submenu_produtos()
        elif opcao == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu_principal()