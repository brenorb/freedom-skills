# Commands

## Save one page with the bundled wrapper

```bash
python3 skills/wayback-archive/scripts/wayback_archive.py save https://example.com
```

## Check availability with the bundled wrapper

```bash
python3 skills/wayback-archive/scripts/wayback_archive.py available https://example.com
```

## Batch-save from a file

```bash
python3 skills/wayback-archive/scripts/wayback_archive.py batch-save --input /absolute/path/to/urls.txt
```

## Official raw endpoints

Save a page:

```bash
curl -I "https://web.archive.org/save/https://example.com"
```

Check the closest archived snapshot:

```bash
curl "https://archive.org/wayback/available?url=https://example.com"
```
