from stock.models import Produto
Produto.objects.all().delete()

import openpyxl
import math
from stock.models import Produto
from datetime import datetime

wb = openpyxl.load_workbook('stock/DadosIniciais.xlsx')
sheet = wb.active

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

    # Marca
    marca = "" if marca is None or (isinstance(marca, float) and math.isnan(marca)) else marca

    # Estoque
    estoque = estoque if estoque != 'null' else 0

    # Preço
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

print("Importação feita com amor e sem erros! 🌟💾")
