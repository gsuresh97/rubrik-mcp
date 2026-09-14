# Running the Rubrik MCP in a container

The Rubrik MCP runs over **stdio**: your MCP client launches `docker run -i --rm …`
as a subprocess and speaks JSON-RPC over stdin/stdout. There is no network
listener to expose or secure.

## Build

```bash
docker build -t rubrik-mcp:0.1.0 .
```

The image is `debian:12-slim`-based (Python 3.11), runs as a non-root user (`mcp`), and sets
`RUBRIK_MCP_CONFIG_DIR=/config` so the policy file and saved workflows live at a stable,
mountable path (see **Config & workflows** below). Dependencies are installed
from the repo's hash-pinned `requirements.txt` with `pip --require-hashes`, so a
build fails if any wheel's hash doesn't match the lockfile.

> The commands here use `0.1.0` as the image tag for concreteness. Substitute the
> version you're building — it's the single source of truth in
> `src/rubrik/__init__.py`.

A hardened, distroless variant is available via a build target — see
[Hardened (GA) image](#hardened-ga-image) below.

## Package as a distributable artifact (no registry)

For offline distribution (e.g. a Beta download), export the image to a tarball
with `docker save` — the customer restores it with `docker load`, no registry
required:

```bash
docker save rubrik-mcp:0.1.0 -o rubrik-mcp.tar
mkdir rubrik-mcp-0.1.0 && mv rubrik-mcp.tar rubrik-mcp-0.1.0/
tar -czf rubrik-mcp-0.1.0.tar.gz rubrik-mcp-0.1.0/
shasum -a 256 rubrik-mcp-0.1.0.tar.gz > rubrik-mcp-0.1.0.tar.gz.sha256
```

Customer side:

```bash
tar -xzf rubrik-mcp-0.1.0.tar.gz
docker load -i rubrik-mcp-0.1.0/rubrik-mcp.tar
docker images | grep rubrik-mcp
```

**Multi-arch:** `docker save` captures only the architecture(s) you built. To
cover both Intel and Apple/ARM, build a multi-arch image
(`docker buildx build --platform linux/amd64,linux/arm64 …`) or ship one tarball
per architecture.

## Configure your MCP client

The client invokes `docker run` instead of a local binary. The recommended way
to register it is `claude mcp add`, because your shell expands `$HOME` so the
config directory defaults to your host `~/.rubrik` (Docker auto-creates it on
first run — no `mkdir` needed) and persists across sessions:

```bash
claude mcp add rubrik -- docker run -i --rm \
  -e RSC_SERVICE_ACCOUNT_FILE=/creds.json \
  -e RUBRIK_MCP_CONFIG_DIR=/config \
  -v "$HOME/.rubrik:/config" \
  -v "$HOME/Downloads/service_account.json:/creds.json:ro" \
  rubrik-mcp:0.1.0
```

Discovery-only usage needs no credential — drop the `RSC_SERVICE_ACCOUNT_FILE`
line and the `/creds.json` mount.

Equivalent raw config (note: an `mcpServers` args array is **not** shell-expanded,
so use an absolute path — `/Users/you/.rubrik`, or `C:/Users/you/.rubrik` on
Windows — in place of `$HOME/.rubrik`):

```json
{
  "mcpServers": {
    "rubrik": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "RSC_SERVICE_ACCOUNT_FILE=/creds.json",
        "-e", "RUBRIK_MCP_CONFIG_DIR=/config",
        "-v", "/Users/you/.rubrik:/config",
        "-v", "/Users/you/Downloads/service_account.json:/creds.json:ro",
        "rubrik-mcp:0.1.0"
      ]
    }
  }
}
```

## Config & workflows (`RUBRIK_MCP_CONFIG_DIR` / `/config`)

The gating policy (`mcp-policy.json`) and saved workflows (`workflows/`) live
under `RUBRIK_MCP_CONFIG_DIR`. The image bakes `ENV RUBRIK_MCP_CONFIG_DIR=/config`, so mounting a
host directory at `/config` is all that's required. We recommend also passing
`-e RUBRIK_MCP_CONFIG_DIR=/config` explicitly in your run command — it's redundant with
the image default but makes the intent self-documenting and keeps the mount
working even if the image's default ever changes:

The recommended default is to mount your host `~/.rubrik` (the same directory a
native install uses), so container and native runs share one config location:

```bash
-e RUBRIK_MCP_CONFIG_DIR=/config -v "$HOME/.rubrik:/config"
```

- **Auto-created:** Docker creates the host directory if it doesn't exist — no
  `mkdir` needed. On first run the server seeds a default `mcp-policy.json`
  (mode `0600`) into it; edit it on the host and restart to change gating. Write
  tools are disabled in that default — set `"writes_enabled": true` to expose them.
- **Persists** across sessions, so `rsc_save_workflow` output and policy edits
  stick. Without any mount, `/config` is an anonymous volume seeded fresh each
  run (edits don't persist).
- **Mount the *directory*, not a file** — bind-mounting a nonexistent *file*
  path makes Docker create a directory there instead.

### Platform notes

- **macOS / Windows (Docker Desktop):** `-v "$HOME/.rubrik:/config"` just works —
  Docker Desktop remaps ownership so the non-root container can write, and
  auto-creates `~/.rubrik` if missing. (Windows PowerShell: use
  `-v "${env:USERPROFILE}\.rubrik:/config"`; note NTFS doesn't enforce the `0600`
  the server sets — use a named volume `-v rubrik-config:/config` if that matters.)
- **Native Linux:** when Docker auto-creates `~/.rubrik` it's owned by **root**,
  and the container runs as non-root (`mcp`, uid `10001`), so seeding into it
  fails. Either pre-create it yourself (`mkdir -p ~/.rubrik`, so it's owned by
  you) or add `--user "$(id -u):$(id -g)"` to the `docker run` args — the latter
  works cleanly because `RUBRIK_MCP_CONFIG_DIR=/config` decouples the config dir from the
  container user's home.

## Hardened (GA) image

For a minimal attack surface, the same `Dockerfile` has a `distroless` build
target (`gcr.io/distroless/python3-debian12:nonroot`): no shell, no package
manager. It shares the dependency-build stage with the default image, so the two
can't drift apart. Build with:

```bash
docker build --target distroless -t rubrik-mcp:0.1.0-distroless .
```

Trade-off: no `docker exec … sh` for debugging. The `/config` directory is
pre-created (uid 65532, matching distroless `nonroot`) in the build stage, so the
anonymous-volume case works without a host mount, same as the default image.

## Uninstall

```bash
docker rmi rubrik-mcp:0.1.0
```
Then remove the `rubrik` entry from your MCP client config.
