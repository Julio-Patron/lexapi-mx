import os

from lex_api_mx import LexApiClient


with LexApiClient(
    base_url=os.environ.get("LEX_API_BASE_URL", "https://api.lexapi.mx"),
    api_key=os.environ["LEX_API_KEY"],
) as client:
    package = client.resolve(
        query="Artículo 1 de la Ley de Concursos Mercantiles",
        norm="lcm",
        limit=5,
        idempotency_key="quickstart-resolve-001",
    )
    print(package["coverage"]["status"])
    for item in package["items"]:
        print(item["citation"]["canonical"], item["version"]["checksum"])
