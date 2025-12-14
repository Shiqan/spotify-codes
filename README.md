# Spotify Codes

Encoding and decoding Spotify codes with Python.
[Spotify Codes](https://www.spotifycodes.com/) are QR-like codes that can be generated to easily share Spotify songs, artists, playlists, and users.

All credits to [How do Spotify Codes work?](https://boonepeter.github.io/posts/2020-11-10-spotify-codes/) and [Spotify Codes - Part 2](https://boonepeter.github.io/posts/spotify-codes-part-2/).

## Getting Started

### Prerequisites

- Python 3.9 or higher

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd spotify-codes
```

2. Create a virtual environment:

(if needed, install `uv` first)
```bash
pip install uv
```

```bash
uv venv
```

3. Activate the virtual environment:
- On macOS/Linux:
```bash
.venv/bin/activate
```
- On Windows:
```bash
.venv\Scripts\activate
```

4. Install dependencies:
```bash
uv pip install -r uv.lock
```

## Development

### Running the Project

```bash
python -m spotify_codes
```

### Running Tests

```bash
pytest
```

### Running linter

```bash
uvx ruff check
```

```bash
uvx ruff format
```

### Adding Dependencies

When you add a new package, install it and update `requirements.txt`:

```bash
uv pip install package-name
uv pip freeze > requirements.txt
uv pip compile requirements.txt -o uv.lock
```

Then commit the updated `requirements.txt` file.

## Project Structure

```
spotify-codes/
├── .venv/
├── spotify_codes/
│   ├── __init__.py
│   ├── encoder.py
│   └── ...etc
├── tests/
│   ├── __init__.py
│   └── test_encoder.py
│   └── ...etc
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Deactivating the Virtual Environment

When you're done working on the project:

```bash
deactivate
```

## License

Licensed under the [MIT License](LICENSE).