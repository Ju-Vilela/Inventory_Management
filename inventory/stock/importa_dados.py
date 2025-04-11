import pandas as pd
from stock.models import Produto
from datetime import datetime

# Lê o arquivo Excel
df = pd.read_excel("DadosIniciais.xlsx")

# Itera sobre cada linha
for _, row in df.iterrows():
    item = row.get("Item")
    categoria = row.get("Categoria")
    marca = row.get("Marca")
    validade_raw = row.get("Validade")
    estoque_raw = row.get("Estoque")
    preco_raw = row.get("Preço")
    vendas = 0

    # Trata a validade
    validade = None
    if isinstance(validade_raw, str):
        try:
            validade = datetime.strptime(validade_raw, "%d/%m/%Y").date()
        except ValueError:
            pass  # deixa como None se a data estiver errada

    # Trata o estoque
    if pd.isna(estoque_raw) or str(estoque_raw).strip().lower() == "null":
        estoque = 0
    else:
        try:
            estoque = int(estoque_raw)
        except ValueError:
            estoque = 0  # Se não der pra converter, assume 0

    # Trata o preço
    preco = 0.0
    if preco_raw:
        try:
            preco = float(str(preco_raw).replace("R$", "").replace(",", "."))
        except ValueError:
            preco = 0.0

    # Cria o produto
    Produto.objects.create(
        item=item,
        categoria=categoria,
        marca=marca or "",
        validade=validade,
        estoque=estoque,
        preco=preco,
        vendas=vendas
    )

print("Importação concluída com sucesso! 🎉")
