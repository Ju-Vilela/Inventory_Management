import openpyxl
from stock.models import Produto
from datetime import datetime

# Caminho correto para o arquivo (ajuste se necessário!)
caminho_arquivo = "stock/DadosIniciais.xlsx"

# Abre a planilha
wb = openpyxl.load_workbook(caminho_arquivo)
sheet = wb.active

# Ignora o cabeçalho
for row in sheet.iter_rows(min_row=2, values_only=True):
    item, categoria, marca, validade, estoque, preco = row

    # Converte a data
    if isinstance(validade, str):
        try:
            validade = datetime.strptime(validade, "%d/%m/%Y").date()
        except:
            validade = None

    Produto.objects.create(
        item=item,
        categoria=categoria,
        marca=marca or "",
        validade=validade,
        estoque=estoque or 0,
        preco=float(str(preco).replace("R$", "").replace(",", ".")) if preco else 0.0
    )

print("✨ Importação concluída com sucesso! ✨")
