# Stitch API Reference

## Other

### `GET /api/v1/health`

<!-- description -->

**Response:** `200`

---

## Oil Gas Fields

### `GET /api/v1/oil-gas-fields/`

<!-- description -->

**Response:** `200`

- array[OGFieldListItemView]

---

### `POST /api/v1/oil-gas-fields/`

<!-- description -->

**Request Body:** `OGFieldResource-Input`

- `id`: integer | null
- `source_data`: array[GemSource | WoodMacSource | RMISource | LLMSource]
- `repointed_to`: integer | null
- `constituents`: array[integer]
- `provenance`: object[string, array[object] | null]
- `view`: OilGasFieldBase | null

**Response:** `200`

- `id`: integer | null
- `source_data`: array[GemSource | WoodMacSource | RMISource | LLMSource]
- `repointed_to`: integer | null
- `constituents`: array[integer]
- `provenance`: object[string, array[object] | null]
- `view`: OilGasFieldBase | null

---

### `GET /api/v1/oil-gas-fields/{id}`

<!-- description -->

**Response:** `200`

- `name`: string | null
- `country`: string | null
- `latitude`: number | null
- `longitude`: number | null
- `name_local`: string | null
- `state_province`: string | null
- `region`: string | null
- `basin`: string | null
- `owners`: array[OilGasOwner] | null
- `operators`: array[OilGasOperator] | null
- `location_type`: string | null
- `production_conventionality`: string | null
- `primary_hydrocarbon_group`: string | null
- `reservoir_formation`: string | null
- `discovery_year`: integer | null
- `production_start_year`: integer | null
- `fid_year`: integer | null
- `field_status`: string | null
- `id`: integer

---

### `GET /api/v1/oil-gas-fields/{id}/detail`

<!-- description -->

**Response:** `200`

- `id`: integer
- `data`: OilGasFieldBase
- `provenance`: object[string, string | null]
- `source_data`: array[GemSource | WoodMacSource | RMISource | LLMSource]

---

### `POST /api/v1/oil-gas-fields/merge`

<!-- description -->

**Request Body:** Body


**Response:** `200`

- `id`: integer | null
- `source_data`: array[GemSource | WoodMacSource | RMISource | LLMSource]
- `repointed_to`: integer | null
- `constituents`: array[integer]
- `provenance`: object[string, array[object] | null]
- `view`: OilGasFieldBase | null

---

## Oil Gas Field Sources

### `GET /api/v1/oil-gas-field-sources/`

<!-- description -->

**Response:** `200`

- array[GemSource | WoodMacSource | RMISource | LLMSource]

---

### `POST /api/v1/oil-gas-field-sources/`

<!-- description -->

**Request Body:** Body


**Response:** `200`

- GemSource | WoodMacSource | RMISource | LLMSource

---

### `GET /api/v1/oil-gas-field-sources/{id}`

<!-- description -->

**Response:** `200`

- GemSource | WoodMacSource | RMISource | LLMSource

---
