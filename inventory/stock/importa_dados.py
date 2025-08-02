from stock.models import Produto
import openpyxl
import uuid

# Limpar todos os produtos existentes (use com cuidado!)
Produto.objects.all().delete()

# Carregar a planilha
wb = openpyxl.load_workbook('stock/DadosIniciais.xlsx')
sheet = wb.active

# Iterar pelas linhas da planilha (assumindo cabeçalho na primeira linha)
for row in sheet.iter_rows(min_row=2, values_only=True):
    # Altere essa linha conforme as colunas REAIS da planilha
    item, categoria, marca, validade, estoque, preco, *resto = row

    # Ignorar linhas em branco
    if not item or str(item).strip() == "":
        continue

    # Tratar marca
    marca = str(marca).strip() if marca and str(marca).strip().lower() != "null" else "sem marca"

    # Tratar estoque
    try:
        estoque = int(estoque) if estoque else 0
    except:
        estoque = 0

    # Tratar preço
    try:
        preco_str = str(preco).replace("R$", "").replace(",", ".")
        preco = float(preco_str) if preco else 0.0
    except:
        preco = 0.0

    # Criar produto (sku e datas serão gerados automaticamente)
    Produto.objects.create(
        item=item.strip(),
        categoria=categoria.strip() if categoria else "Sem Categoria",
        marca=marca,
        estoque=estoque,
        estoque_minimo=1,  # defina como quiser ou adicione coluna depois
        preco=preco,
        ativo=True
    )

print("Importacao feita com sucesso!")
