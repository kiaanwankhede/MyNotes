# Glossary
> lead: The Pydantic terms from this book in one line each, grouped by theme, with the chapter where each is explained. Use the search box to jump to a term.
meta: About 70 terms | Links go to the chapter

## Models and validation

| Term | One line | Chapter |
| --- | --- | --- |
| **`BaseModel`** | A class whose fields are validated when you create it | [2](#pydantic-p2) |
| **Validation** | Checking and converting input so the object matches its declared types and constraints | [2](#pydantic-p2) |
| **Parsing** | The docs' word for validating a JSON string | [2](#pydantic-p2) |
| **Coercion (lax mode)** | Converting reasonable input, such as `"28"` to `28`; `"28eight"` and `28.5` for an `int` fail | [2](#pydantic-p2) |
| **Strict mode** | Turns conversion off: `"123"` is no longer an `int` | [7](#pydantic-p7) |
| **`ValidationError`** | One error that bundles every problem found in a validation pass | [9](#pydantic-p9) |
| **`model_validate` / `model_validate_json`** | Validate a dict / a JSON string or bytes | [2](#pydantic-p2) |
| **`model_dump` / `model_dump_json`** | Back to a dict / a JSON string | [5](#pydantic-p5) |
| **`model_copy`** | Copy a model; updates are not validated and the copy is shallow unless `deep=True` | [2](#pydantic-p2) |
| **`model_construct`** | Build without validation, for data you already trust | [2](#pydantic-p2) |
| **`model_fields_set`** | Which fields were explicitly provided | [2](#pydantic-p2), [5](#pydantic-p5) |
| **`extra`** | What to do with unknown keys: ignore (default), `forbid` or `allow` | [2](#pydantic-p2) |
| **`frozen`** | Blocks assignment; a "faux" immutability since nested dicts can still change | [2](#pydantic-p2) |
| **`from_attributes`** | Read fields from attributes of any object, such as an ORM row | [2](#pydantic-p2) |
| **Private attribute** | A name starting with an underscore; not a field | [2](#pydantic-p2) |
| **`@dataclass`** | Standard-library class that stores values but does not validate them | [2](#pydantic-p2) |
| **Pydantic dataclass** | A dataclass with Pydantic validation, without `BaseModel`; no `model_validate`, wrap in `TypeAdapter` | [6](#pydantic-p6) |
| **`TypeAdapter`** | Validate, serialize and build a schema for any type without a model; create it once and reuse it | [6](#pydantic-p6) |
| **`ConfigDict`** | Settings that control a model's behaviour (`model_config` or class arguments) | [2](#pydantic-p2) |
| **Configuration boundary** | Models and Pydantic dataclasses do not pass config to nested models; stdlib dataclasses do | [2](#pydantic-p2) |

## Fields and types

| Term | One line | Chapter |
| --- | --- | --- |
| **`Field()`** | Adds constraints, defaults, aliases and metadata to a field | [3](#pydantic-p3) |
| **`Annotated`** | The docs' preferred way to attach `Field(...)` or validators to a type | [3](#pydantic-p3) |
| **Constraint** | `gt`, `ge`, `lt`, `le`, `multiple_of`, `min_length`, `max_length`, `pattern`, `max_digits`, `decimal_places` | [3](#pydantic-p3) |
| **`default_factory`** | A callable that makes a default; since 2.10 it may take the validated data | [3](#pydantic-p3) |
| **`validate_default`** | Makes Pydantic check default values, which it does not by default | [3](#pydantic-p3) |
| **Alias** | Another name for a field: `alias`, `validation_alias`, `serialization_alias` | [3](#pydantic-p3) |
| **`AliasPath` / `AliasChoices`** | Read a value from a nested path / try several input names, earlier ones first | [3](#pydantic-p3) |
| **Alias generator** | Names every field at once: `to_camel`, `to_pascal`, `to_snake` or your own | [3](#pydantic-p3) |
| **`SecretStr`** | Masks a value in output and logs; read it with `.get_secret_value()` | [3](#pydantic-p3), [8](#pydantic-p8) |
| **`EmailStr` / `HttpUrl`** | Email and URL validation (`EmailStr` needs `pydantic[email]`) | [3](#pydantic-p3) |
| **`PositiveInt`** | Shortcut for `gt=0` | [3](#pydantic-p3) |
| **`Literal`** | Allows only the listed values | [7](#pydantic-p7), [11](#pydantic-p11) |
| **`OnErrorOmit` / `FailFast`** | Drop invalid items instead of failing / stop at the first bad item | [3](#pydantic-p3) |
| **Union** | A value that may be one of several types; only one member needs to validate | [6](#pydantic-p6) |
| **Smart mode** | Default union mode: tries members and picks the best match (valid fields set, then exactness) | [6](#pydantic-p6) |
| **Left to right mode** | Tries members in order, first success wins (`union_mode='left_to_right'`) | [6](#pydantic-p6) |
| **Discriminated union** | Picks the member from a tag field, so validation is faster and errors are shorter | [6](#pydantic-p6) |

## Validators and serialization

| Term | One line | Chapter |
| --- | --- | --- |
| **`field_validator`** | Checks one field; returns the value or raises `ValueError` | [4](#pydantic-p4) |
| **after / before / plain / wrap** | Run after Pydantic's check / on raw input / replace it / around it | [4](#pydantic-p4) |
| **`model_validator`** | Checks across fields; an after-validator must return `self` | [4](#pydantic-p4) |
| **`ValidationInfo`** | Extra argument carrying earlier fields, `context`, `mode` and `field_name` | [4](#pydantic-p4) |
| **Validation context** | Data passed with `model_validate(..., context=...)` for validators to read | [4](#pydantic-p4), [11](#pydantic-p11) |
| **`@computed_field`** | A read-only property included in dumps and the serialization schema | [5](#pydantic-p5) |
| **`mode="json"`** | Dump only JSON-compatible types (a tuple becomes a list) | [5](#pydantic-p5) |
| **`exclude_unset`** | Dump only fields the caller set; the key to PATCH-style updates | [5](#pydantic-p5) |
| **`field_serializer` / `model_serializer`** | Change how one field or a whole model is written | [5](#pydantic-p5) |
| **Serialize as any** | Opt in to serializing a subclass's extra fields | [5](#pydantic-p5) |
| **Forward reference / `model_rebuild`** | A string annotation for a class defined later / finish the model once it exists | [6](#pydantic-p6) |

## JSON Schema, settings, errors and LLMs

| Term | One line | Chapter |
| --- | --- | --- |
| **JSON Schema** | A description of a model's data from `model_json_schema()`; a dict, not a string | [7](#pydantic-p7) |
| **`$defs` / `$ref`** | Where nested models live in the schema and how they are referenced | [7](#pydantic-p7) |
| **Validation vs serialization schema** | Describes accepted input / describes the output | [7](#pydantic-p7) |
| **`BaseSettings`** | A model filled from environment variables, `.env` files and secrets | [8](#pydantic-p8) |
| **`env_nested_delimiter`** | `DB__HOST` fills `db.host` when set to `"__"` | [8](#pydantic-p8) |
| **`errors()`** | A list of dicts with `type`, `loc`, `msg`, `input`, `ctx` and `url` | [9](#pydantic-p9) |
| **`loc`** | The path to the bad value, such as `('items', 1, 'value')` | [9](#pydantic-p9) |
| **Error `type`** | Machine-readable id such as `missing`, `greater_than`, `int_parsing` | [9](#pydantic-p9) |
| **`response_model`** | FastAPI option that validates and filters the output with a model | [10](#pydantic-p10) |
| **Request body model** | A Pydantic parameter FastAPI reads from the JSON body | [10](#pydantic-p10) |
| **Retry loop** | Feed the `ValidationError` text back to the model and ask again, up to a limit | [11](#pydantic-p11) |
| **Shape, not correctness** | Validation checks type and shape, not whether the facts are right | [11](#pydantic-p11) |
