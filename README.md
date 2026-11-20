# Internet speed checker

A small Python 3 command-line tool that downloads a URL ten times in sequence. It waits for each response body to finish before starting the next request, then prints the total downloaded data, average request time, and average download speed.

## Requirements

- Python 3.10 or newer
- No third-party packages

## Run

```bash
python3 speedtest.py "https://example.com/large-image.jpg"
```

Use a stable, publicly accessible file URL for a useful measurement. The script follows the server's response (including redirects), reads the body in chunks, and uses a 30-second timeout for each request.

## Output units

- Downloaded data: bytes and decimal megabytes (MB, 1 MB = 1,000,000 bytes).
- Average request time: seconds.
- Download speed: decimal megabytes per second (MB/s), calculated as total bytes downloaded divided by total time spent downloading all ten responses. This is the average across the full run, including server and network latency during those requests.
