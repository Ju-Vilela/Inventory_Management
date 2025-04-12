from stock.models import Produto
import openpyxl
import math
from datetime import datetime

# Limpar todos os produtos
Produto.objects.all().delete()

# Carregar a planilha
wb = openpyxl.load_workbook('stock/DadosIniciais.xlsx')
sheet = wb.active

# Iterar pelas linhas da planilha
for row in sheet.iter_rows(min_row=2, values_only=True):
    item, categoria, marca, validade, estoque, preco = row

    # Pula se o item estiver vazio ou só com espaços
    if not item or str(item).strip() == "":
        continue

    # Converte validade
    if isinstance(validade, str):
        try:
            validade = datetime.strptime(validade, "%d/%m/%Y").date()
        except:
            validade = None

    # Marca: se for 'null' ou vazio, define como 'sem marca'
    if marca == 'null' or not marca:
        marca = 'sem marca'

    # Estoque: se for 'null', define como 0
    estoque = estoque if estoque != 'null' else 0

    # Preço: converte para float se tiver valor
    preco = float(str(preco).replace("R$", "").replace(",", ".")) if preco else 0.0

    # Criação do produto com vendas=0
    Produto.objects.create(
        item=item,
        categoria=categoria,
        marca=marca,
        validade=validade,
        estoque=estoque,
        preco=preco,
        vendas=0
    )

print("Importacao feita com amor e sem erros!")
