import pytest

from app.dart.targets import TargetList, load_targets


def company(corp_code: object = "00126380") -> dict:
    return {"corp_code": corp_code, "name": "테스트", "role": "테스트"}


def test_load_real_file():
    targets = load_targets()

    assert len(targets) >= 5
    assert targets[0].corp_code == "00126380"


@pytest.mark.parametrize("bad_code", ["0012638", "001263800", "0012638A", 126380])
def test_invalid_corp_code(bad_code):
    with pytest.raises(ValueError):
        TargetList.model_validate({"companies": [company(bad_code)]})


def test_duplicate_corp_code():
    data = {"companies": [company(), company()]}

    with pytest.raises(ValueError, match="중복"):
        TargetList.model_validate(data)


def test_empty_list():
    with pytest.raises(ValueError):
        TargetList.model_validate({"companies": []})
