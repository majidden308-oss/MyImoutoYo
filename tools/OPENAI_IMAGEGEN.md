# OpenAI Background Generation

This project can generate missing Ren'Py background images directly with the OpenAI Images API.

## Files

- `tools/openai_background_manifest.json`: prompt manifest for each scene background.
- `tools/generate_openai_backgrounds.py`: zero-dependency Python script that calls `POST /v1/images/generations`.

## Requirements

- Python 3.10+
- `OPENAI_API_KEY` environment variable

## Usage

```powershell
$env:OPENAI_API_KEY="your_api_key"
python tools/generate_openai_backgrounds.py --dry-run
python tools/generate_openai_backgrounds.py --overwrite
```

Generate only one scene:

```powershell
python tools/generate_openai_backgrounds.py --only "bg livingroom" --overwrite
python tools/generate_openai_backgrounds.py --only bg_livingroom.png --overwrite
```

## Output

By default, files are written to:

`game/images`

This matches the fallback image definitions in `game/placeholders.rpy`.

## API Notes

- Default model: `gpt-image-1`
- Endpoint: `https://api.openai.com/v1/images/generations`
- Response handling: requests `b64_json` and writes decoded PNG bytes to disk

Official docs:

- https://platform.openai.com/docs/guides/images/image-generation
- https://platform.openai.com/docs/api-reference/images/create
