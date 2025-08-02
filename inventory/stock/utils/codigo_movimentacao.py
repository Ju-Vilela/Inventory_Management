from datetime import datetime

TIPOS_ENTRADA = {
    'compra': 'CO',
    'ajuste': 'AJ',
    'devolucao': 'DV',
    'transferencia': 'TR',
    'correcao': 'CR',
    'outro': 'TP',
}

TIPOS_SAIDA = {
    'venda': 'VE',
    'ajuste': 'AJ',
    'perda': 'PD',
    'transferencia': 'TR',
    'correcao': 'CR',
    'outro': 'TP',
}

def gerar_codigo_movimentacao(tipo_geral, subtipo, numero_seq=1):
    prefixo = 'E' if tipo_geral.lower() == 'entrada' else 'S'
    mapa = TIPOS_ENTRADA if prefixo == 'E' else TIPOS_SAIDA
    subtipo_sigla = mapa.get(subtipo.lower(), 'TP')
    data = datetime.now().strftime('%d%m%y')
    seq_str = f"{numero_seq:03d}"
    base = f"{prefixo}{subtipo_sigla}{data}{seq_str}"
    total = sum((i + 1) * ord(char) for i, char in enumerate(base))
    dv = total % 10
    return f"{base}{dv}"

def validar_codigo(codigo):
    if len(codigo) != 12:
        return False
    base = codigo[:-1]
    dv_informado = int(codigo[-1])
    total = sum((i + 1) * ord(char) for i, char in enumerate(base))
    dv_calculado = total % 10
    return dv_calculado == dv_informado
