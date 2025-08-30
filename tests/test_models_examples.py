import json
from pathlib import Path

from spypointapi.models.photo import PhotoAllResponse


def test_models_preserve_unknown_keys():
    data = json.loads(Path("tests/fixtures/POST_api_v3_photo_all.json").read_text())
    resp = PhotoAllResponse.model_validate(data)
    # ensure all top-level keys present either in model fields or in __pydantic_extra__
    for k in data.keys():
        assert (k in resp.model_fields) or (k in resp.__pydantic_extra__)
