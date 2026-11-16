import io
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import httpx
from pydantic import BaseModel

BASE_URL = "https://opendart.fss.or.kr/api"
CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "dart"


class CorpCode(BaseModel):
    corp_code: str
    corp_name: str
    stock_code: str | None


class DartClient:
    def __init__(self, api_key: str, http: httpx.AsyncClient, cache_dir: Path = CACHE_DIR) -> None:
        self._api_key = api_key
        self._http = http
        self._cache_dir = cache_dir

    async def corp_codes(self) -> list[CorpCode]:
        path = self._cache_dir / "CORPCODE.xml"
        if not path.exists():
            response = await self._http.get(
                f"{BASE_URL}/corpCode.xml", params={"crtfc_key": self._api_key}
            )
            response.raise_for_status()
            if not response.content.startswith(b"PK"):
                raise RuntimeError(f"not zip response: {response.text[:200]}")
            with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
                xml_bytes = archive.read(archive.namelist()[0])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(xml_bytes)
        return parse_corp_codes(path.read_bytes())


def parse_corp_codes(xml_bytes: bytes) -> list[CorpCode]:
    root = ElementTree.fromstring(xml_bytes)
    corps: list[CorpCode] = []
    for item in root.iter("list"):
        stock_code = (item.findtext("stock_code") or "").strip()
        corps.append(
            CorpCode(
                corp_code=(item.findtext("corp_code") or "").strip(),
                corp_name=(item.findtext("corp_name") or "").strip(),
                stock_code=stock_code or None,
            )
        )
    return corps
