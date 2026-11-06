import requests


IBGE_BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"
VALID_UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


class IBGEServiceError(Exception):
    pass


def _get_json(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise IBGEServiceError("Falha ao consultar o serviço do IBGE.") from exc


def list_municipalities(uf):
    if uf not in VALID_UFS:
        raise ValueError("UF inválida.")

    data = _get_json(f"{IBGE_BASE_URL}/estados/{uf}/municipios")
    if not isinstance(data, list):
        raise IBGEServiceError("Resposta inesperada do serviço do IBGE.")

    municipalities = []
    for municipality in data:
        if not isinstance(municipality, dict) or "id" not in municipality or "nome" not in municipality:
            raise IBGEServiceError("Resposta inesperada do serviço do IBGE.")
        municipalities.append(
            {"id": municipality["id"], "nome": municipality["nome"]}
        )
    return municipalities


def municipality_exists(code):
    url = f"{IBGE_BASE_URL}/municipios/{code}"
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as exc:
        raise IBGEServiceError("Falha ao consultar o serviço do IBGE.") from exc

    if response.status_code == 404:
        return False

    try:
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise IBGEServiceError("Falha ao consultar o serviço do IBGE.") from exc

    return isinstance(data, dict) and data.get("id") == code
