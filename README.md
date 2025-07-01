# File Downloader by Extension and Domain

A Python command-line tool that downloads files with a specific extension from a given domain using Google's Custom Search API.

## Features

- Search for files by extension on any domain using Google Custom Search API
- Automatic file downloading with progress tracking
- API credential management with secure storage
- Fast and reliable using Google's official API
- Respects rate limits and implements proper error handling
- Duplicate detection to avoid re-downloading files

## Prerequisites

### 1. Install `uv`

`uv` is a fast Python package installer and resolver, written in Rust.

#### macOS
```bash
# Using Homebrew
brew install uv

# Or using curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```powershell
# Using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using winget
winget install --id=astral-sh.uv -e
```

#### Linux
```bash
# Using curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip (if you have Python installed)
pip install uv
```

### 2. Google API Setup

You'll need to set up Google Custom Search API credentials:

1. **Get an API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or select an existing one)
   - Enable the "Custom Search API"
   - Go to "Credentials" → "Create Credentials" → "API Key"
   - Copy your API key

2. **Create a Search Engine:**
   - Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Click "Add" to create a new search engine
   - In "Sites to search", you can add specific sites or leave it empty
   - After creation, go to "Edit search engine" → "Setup"
   - Turn ON "Search the entire web"
   - Copy your Search Engine ID (cx parameter)

## Installation

1. Clone or download the repository.

2. Install dependencies using `uv`:
```bash
# This creates a virtual environment and installs dependencies
uv sync
```

## Usage

### Basic Usage

Run the script with `uv run`:

```bash
# Search and download PDF files from a domain
uv run python file-downloader.py example.com pdf
```

On first run, you'll be prompted to enter your API credentials.

### Platform-Specific Examples

#### macOS / Linux
```bash
# Download 20 PDF files to a specific directory
uv run python file-downloader.py puolustusvoimat.fi pdf -n 20 -d ~/Downloads/pdfs

# Save credentials for future use
uv run python file-downloader.py example.com pdf --save-credentials

# Use specific API credentials
uv run python file-downloader.py example.com docx \
    --api-key "YOUR_API_KEY" \
    --search-engine-id "YOUR_SEARCH_ENGINE_ID"
```

#### Windows (PowerShell)
```powershell
# Download 20 PDF files to a specific directory
uv run python file-downloader.py puolustusvoimat.fi pdf -n 20 -d C:\Downloads\pdfs

# Save credentials for future use
uv run python file-downloader.py example.com pdf --save-credentials

# Use specific API credentials
uv run python file-downloader.py example.com docx `
    --api-key "YOUR_API_KEY" `
    --search-engine-id "YOUR_SEARCH_ENGINE_ID"
```

#### Windows (Command Prompt)
```cmd
:: Download 20 PDF files to a specific directory
uv run python file-downloader.py puolustusvoimat.fi pdf -n 20 -d C:\Downloads\pdfs

:: Save credentials for future use
uv run python file-downloader.py example.com pdf --save-credentials

:: Use specific API credentials
uv run python file-downloader.py example.com docx ^
    --api-key "YOUR_API_KEY" ^
    --search-engine-id "YOUR_SEARCH_ENGINE_ID"
```

### Command-Line Options

```
positional arguments:
  domain                Domain name to search (e.g., puolustusvoimat.fi)
  extension             File extension to search for (e.g., pdf)

optional arguments:
  -h, --help            Show this help message and exit
  -n NUMBER, --number NUMBER
                        Number of files to download (default: 10)
  -d DIRECTORY, --directory DIRECTORY
                        Directory to save files (default: current directory)
  --api-key API_KEY     Google Custom Search API key
  --search-engine-id SEARCH_ENGINE_ID
                        Google Custom Search Engine ID
  --save-credentials    Save API credentials for future use
```

## Examples

### Download Different File Types

```bash
# PDFs
uv run python file-downloader.py scientificamerican.com pdf -n 5

# Word documents
uv run python file-downloader.py microsoft.com docx -n 10

# Excel files
uv run python file-downloader.py data.gov xlsx -n 15

# PowerPoint presentations
uv run python file-downloader.py slideshare.net pptx -n 5
```

### Organize Downloads by Type

```bash
# Create organized directory structure
mkdir -p downloads/{pdfs,docs,spreadsheets}

# Download different file types to specific folders
uv run python file-downloader.py company.com pdf -d downloads/pdfs
uv run python file-downloader.py company.com docx -d downloads/docs
uv run python file-downloader.py company.com xlsx -d downloads/spreadsheets
```

## Managing the Virtual Environment

`uv` automatically creates and manages a virtual environment for you. Here are some useful commands:

```bash
# Install/sync dependencies
uv sync

# Add a new dependency
uv add package-name

# Remove a dependency
uv remove package-name

# Run any command in the virtual environment
uv run python script.py

# Show current environment info
uv pip list
```

## Credential Storage

When you use the `--save-credentials` flag, your API credentials are saved to `google_api_config.json` in the current directory. This file contains:

```json
{
  "api_key": "YOUR_API_KEY",
  "search_engine_id": "YOUR_SEARCH_ENGINE_ID"
}
```

**Security Note:** The file `google_api_config.json` is included in `.gitignore` to avoid accidentally committing your credentials.

## API Limits and Pricing

- **Free Tier:** 100 queries per day (each query returns up to 10 results)
- **Paid Tier:** $5 per 1,000 queries beyond the free tier
- **Rate Limits:** The tool handles rate limiting automatically

## Troubleshooting

### Common Issues

1. **"API key not valid" error:**
   - Ensure you've enabled the Custom Search API in Google Cloud Console
   - Check that your API key is correctly copied
   - Verify the API key has no IP restrictions that block your current IP

2. **"No files found" message:**
   - Verify the domain has files of the specified type
   - Check if your Search Engine is set to "Search the entire web"
   - Try a broader search by using a more general domain

3. **Rate limiting errors:**
   - You've exceeded the daily free tier limit (100 queries)
   - Wait until the next day or upgrade to a paid plan

4. **Permission errors on Windows:**
   - Run the command prompt or PowerShell as Administrator
   - Ensure you have write permissions to the download directory

### Platform-Specific Issues

#### macOS
- If `uv` command is not found after installation, add it to your PATH:
  ```bash
  echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
  source ~/.zshrc
  ```

#### Windows
- If you get execution policy errors in PowerShell:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

#### Linux
- If you get permission denied errors:
  ```bash
  chmod +x ~/.cargo/bin/uv
  ```

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details.

## Disclaimer

- Always respect robots.txt and website terms of service
- Only download files you have permission to access
- Be mindful of the website's bandwidth and don't abuse the service
- This tool is for legitimate use only
