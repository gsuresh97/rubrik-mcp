# Rubrik MCP — container image.
#
# stdio transport: the MCP client launches `docker run -i --rm ... rubrik-mcp`
# and speaks JSON-RPC over stdin/stdout. See docs/docker.md for build,
# packaging (docker save -> .tar.gz), and client configuration.
#
# NOTE: pin the base image by digest before release, e.g.
#   FROM python:3.12-slim@sha256:<digest>
FROM python:3.12-slim

# Non-root runtime user, and a stable config dir it owns.
RUN useradd --create-home --uid 10001 mcp \
 && mkdir -p /config \
 && chown mcp:mcp /config

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir . && rm -rf /root/.cache

USER mcp

# Relocate the MCP config dir (mcp-policy.json + workflows/) to a stable,
# mountable path independent of the user's home. Mount a volume at /config to
# persist and (auto-)seed the policy and saved workflows across runs.
ENV RUBRIK_MCP_CONFIG_DIR=/config
VOLUME ["/config"]

ENTRYPOINT ["rubrik-mcp"]
