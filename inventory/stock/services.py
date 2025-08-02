
# from django.db.models import Sum
# from .models import ItemEntrada, ItemSaida

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


# def calcular_estoque_atual(produto_id):
#     entradas = ItemEntrada.objects.filter(produto_id=produto_id).aggregate(total=Sum('quantidade'))['total'] or 0
#     saidas = ItemSaida.objects.filter(produto_id=produto_id).aggregate(total=Sum('quantidade'))['total'] or 0
#     return entradas - saidas
