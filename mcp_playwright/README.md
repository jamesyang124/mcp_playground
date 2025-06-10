# MCP Playwright

wrap as docker container to avoid pollution of host.

build with docker:

```sh
docker build -t mcp_playwright .
```

setup vs code `settings.json` as following:

```json
"mcp": {
    "servers": {
        "mcp_playwright": {
            "command": "docker",
            "args": [
                "exec",
                "-i",
                "mcp_playwright_container",
                "uv",
                "run",
                "main.py"
            ],
            "env": {}
        }
    }
}
```

then run docker-compose:

```sh
docker-compose up -d --build
```

start/restart mcp_playwright in `settings.json` to verify its running result.

then we should be able to prompt as following:

```
mcp server already start by docker container, please run following prompt as fresh start:
go visit `https://github.com/modelcontextprotocol/servers/blob/main/src/fetch/src/mcp_server_fetch` url with playwright, then click current visible text 'server.py' and wait for navigate to its page, then take a screanshot for that page content
```