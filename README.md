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
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   - On Windows:
   ```bash
   venv\Scripts\activate
   ```

   You should see `(venv)` in your terminal prompt when it's active.

4. Install dependencies:
```bash
pip install -r requirements.txt
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

### Adding Dependencies

When you add a new package, install it and update `requirements.txt`:

```bash
pip install package_name
pip freeze > requirements.txt
```

Then commit the updated `requirements.txt` file.

## Project Structure

```
spotify-codes/
├── venv/
├── spotify_codes/
│   ├── __init__.py
│   └── main.py
│   └── ...etc
├── tests/
│   ├── __init__.py
│   └── test_main.py
│   └── ...etc
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