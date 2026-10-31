# Cheat sheet
> lead: The Pydantic patterns on one page. Every item links back to the chapter that explains it, and every line of behaviour here was checked against real Pydantic (see the home page).
meta: Quick reference | Code is condensed. See the chapters for the full versions

## A model in one picture ([Ch 2](#pydantic-p2), [Ch 3](#pydantic-p3))

```python
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, SecretStr, computed_field, field_validator, model_validator

class Applicant(BaseModel):
    model_config = ConfigDict(extra="forbid")            # reject unknown keys
    name: str = Field(min_length=2, max_length=100)
    years: Annotated[int, Field(ge=0, le=50)]
    level: Literal["junior", "senior"] = "junior"       # a default makes it optional
    api_key: SecretStr | None = None

    @field_validator("name")
    @classmethod
    def tidy(cls, v: str) -> str:                       # one field; return the value
        return v.strip()

    @model_validator(mode="after")
    def rules(self):                                    # across fields; return self
        return self

    @computed_field
    @property
    def tier(self) -> str:                              # read-only, appears in dumps
        return "mid" if self.years >= 2 else "junior"
```

## Calls to remember ([Ch 2](#pydantic-p2), [Ch 5](#pydantic-p5))

| Need | Call |
| --- | --- |
| Validate a dict / JSON | `Model.model_validate(d)` / `Model.model_validate_json(s)` |
| Back to dict / JSON | `m.model_dump()` / `m.model_dump_json()` |
| JSON-safe dict | `m.model_dump(mode="json")` |
| Only what the caller sent | `m.model_dump(exclude_unset=True)` |
| Hide / show fields | `exclude=`, `include=`, `Field(exclude=True)`, `exclude_none=True` |
| Output with aliases | `m.model_dump(by_alias=True)` |
| Copy with changes | `m.model_copy(update={...})` (not validated) |
| No validation (trusted data) | `Model.model_construct(...)` |
| Schema | `Model.model_json_schema()` (a dict) |
| Any type | `TypeAdapter(list[int]).validate_python(x)`; create once, reuse |

## Rules that catch people out

- Unknown keys are **ignored** by default; use `extra="forbid"` for LLM schemas.
- `"25"` becomes `25` for an `int`, but `12345` is **not** turned into `"12345"` for a `str`.
- Defaults are **not validated** unless `validate_default=True` (in `BaseSettings` they are).
- A validator must **return the value**; forgetting makes the field `None`.
- Raise `ValueError`, never `ValidationError`, inside a validator.
- Cleaning raw text needs `mode="before"`; the default (after) never sees it.
- Two methods with the same name: only the last one survives.
- A cross-field rule needs `model_validator`, not `field_validator`.
- A model validator is skipped if a field already failed.
- Config does not pass into nested **models**; it does pass into stdlib dataclasses.
- `dump_json` on `TypeAdapter` returns **bytes**; `model_dump_json` returns a `str`.

## Validators ([Ch 4](#pydantic-p4))

| Mode | Runs | Use |
| --- | --- | --- |
| after (default) | after Pydantic's check | value has the right type |
| before | on raw input | clean `"5 years"` to `5` |
| plain | instead of Pydantic's check | bad input can pass |
| wrap | around it, with a `handler` | catch errors, retry |

Order on one field: before and wrap run right to left, then after runs left to right. All field validators run before the model validator.

## Unions ([Ch 6](#pydantic-p6))

Smart mode is the default. Use `Field(discriminator="kind")` with a `Literal` tag for speed and short errors; `Discriminator` plus `Tag` for a callable.

## Errors ([Ch 9](#pydantic-p9))

```python
try:
    Model(**data)
except ValidationError as e:
    for err in e.errors():            # type, loc, msg, input, ctx, url
        print(err["loc"], err["type"], err["msg"])
```

## Settings ([Ch 8](#pydantic-p8))

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    api_key: SecretStr
    debug: bool = False
```

Environment beats `.env` beats the secrets directory. `os.getenv("DEBUG")` of `"false"` is truthy; a `bool` field is not.

## FastAPI and LLMs ([Ch 10](#pydantic-p10), [Ch 11](#pydantic-p11))

- A Pydantic parameter is the **body**; a simple type is a **query** parameter; a name in the path is a **path** parameter.
- `response_model=Out` filters the output (keeps `password` out); invalid output is a 500, bad input a 422.
- PATCH: `item.model_dump(exclude_unset=True)` then `stored.model_copy(update=...)`.
- LLM output: schema from `model_json_schema()` with `extra="forbid"`, validate the reply, on `ValidationError` send `str(e)` back and retry with a **cap**. Valid shape does not mean true facts.
