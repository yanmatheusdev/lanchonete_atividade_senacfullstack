"""Funções de acesso à API pública do IBGE."""
import requests

BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"
TIMEOUT = 10  # segundos
UFS_VALIDAS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


class IBGEIndisponivel(Exception):
    """IBGE fora do ar, lento demais ou com resposta inesperada."""


def _get(url):
    try:
        resposta = requests.get(url, timeout=TIMEOUT)
        resposta.raise_for_status()
        return resposta.json()
    except (requests.RequestException, ValueError) as erro:
        raise IBGEIndisponivel(str(erro)) from erro


def listar_municipios(uf):
    """Retorna a lista de municípios da UF, ou None se a UF não existir."""
    url = f"{BASE_URL}/estados/{uf}/municipios"
    try:
        resposta = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException as erro:
        raise IBGEIndisponivel(str(erro)) from erro

    if resposta.status_code == 404:
        return None
    try:
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.RequestException, ValueError) as erro:
        raise IBGEIndisponivel(str(erro)) from erro

    # UF inexistente: o IBGE pode devolver 200 com lista vazia
    if not dados:
        return None
    return dados


def municipio_existe(codigo_ibge):
    """True se o código existe no IBGE, False se não existe."""
    dados = _get(f"{BASE_URL}/municipios/{codigo_ibge}")
    return bool(dados)
