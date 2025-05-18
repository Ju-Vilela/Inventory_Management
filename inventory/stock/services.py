def atualizar_estoque(produto, quantidade, tipo):
    if tipo == 'Entrada':
        produto.estoque += quantidade
    elif tipo == 'Saida':
        if produto.estoque < quantidade:
            raise ValueError("Estoque insuficiente, minha flor. Bora revisar isso?")
        produto.estoque -= quantidade
    else:
        raise ValueError("Tipo de movimentação inválido. Use 'Entrada' ou 'Saída'.")

    produto.save()