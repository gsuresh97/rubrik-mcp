# Rubrik MCP — container image.
#
# stdio transport: the MCP client launches `docker run -i --rm ... rubrik-mcp`
# and speaks JSON-RPC over stdin/stdout. See docs/docker.md for build,
# packaging (docker save -> .tar.gz), and client configuration.
#
# Two targets share ONE dependency-build stage, so their runtime setup can't
# drift apart:
#   docker build -t rubrik-mcp:0.1.0 .                                   # slim (default)
#   docker build --target distroless -t rubrik-mcp:0.1.0-distroless .    # hardened GA
#
# The base is Debian 12 (bookworm), whose apt Python is 3.11 — the SAME build
# used by gcr.io/distroless/python3-debian12. Building the venv against Debian's
# Python (not the python.org build in the python:* images) is what lets one venv
# run in both the slim runtime and distroless: the interpreter path (/usr/bin)
# and libpython (/usr/lib) line up in both. A python:3.11-slim venv would fail
# in distroless with "libpython3.11.so.1.0: cannot open shared object file".
#
# NOTE: pin the base images by digest before release, e.g.
#   FROM debian:12-slim@sha256:<digest>

# ---- build: hash-verified deps + the package, into a self-contained venv ----
FROM debian:12-slim AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv python3-pip ca-certificates \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# Install dependencies FIRST, from the hash-pinned lockfile export, so this
# layer stays cached across source-only changes. --require-hashes makes the
# build fail if any wheel's hash doesn't match requirements.txt.
COPY requirements.txt ./
# Debian's apt pip is too old to resolve extras (e.g. pyjwt[crypto]) under
# --require-hashes, so bump the installer first. This upgrades only pip (build
# tooling), not any runtime dependency; the app deps below stay hash-verified.
RUN python3 -m venv /venv \
 && /venv/bin/pip install --no-cache-dir --upgrade "pip==24.3.1" \
 && /venv/bin/pip install --no-cache-dir --require-hashes -r requirements.txt

# Then install the package itself, with deps already satisfied above.
COPY . /app
RUN /venv/bin/pip install --no-cache-dir --no-deps . \
 && rm -rf /root/.cache

# Pre-create the config dir in the build stage. The distroless final stage has
# no shell to mkdir/chown it, so both targets COPY it from here. Owned by uid
# 65532 to match distroless 'nonroot'; the slim stage re-chowns to its own user.
RUN mkdir -p /config && chown 65532:65532 /config

# ---- distroless: hardened GA runtime — no shell, no package manager ----
FROM gcr.io/distroless/python3-debian12:nonroot AS distroless
COPY --from=build /venv /venv
COPY --from=build --chown=65532:65532 /config /config
ENV PATH="/venv/bin:$PATH" \
    RUBRIK_MCP_CONFIG_DIR=/config
VOLUME ["/config"]
# distroless 'nonroot' runs as uid 65532; /config is an anonymous volume unless
# a host dir is mounted (see docs/docker.md for the ownership note).
ENTRYPOINT ["/venv/bin/rubrik-mcp"]

# ---- runtime (default): Debian slim with a shell, for dev/Beta convenience ----
FROM debian:12-slim AS runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY --from=build /venv /venv
COPY --from=build /config /config
# Non-root runtime user that owns the config dir.
RUN useradd --create-home --uid 10001 mcp \
 && chown -R mcp:mcp /config
USER mcp
ENV PATH="/venv/bin:$PATH" \
    RUBRIK_MCP_CONFIG_DIR=/config
VOLUME ["/config"]
ENTRYPOINT ["rubrik-mcp"]
