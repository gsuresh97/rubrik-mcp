#!/usr/bin/env bash
# install.sh — installs rubrik-mcp for the current platform.
# Usage: curl -fsSL https://rubrikinc.github.io/rubrik-mcp/install.sh | bash
set -euo pipefail

REPO="rubrikinc/rubrik-mcp"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"
BINARY="rubrik-mcp"

# ── Detect OS ─────────────────────────────────────────────────────────────────
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "${OS}" in
  darwin)  OS="darwin" ;;
  linux)   OS="linux"  ;;
  *)
    echo "error: unsupported OS '${OS}'" >&2
    echo "       Download manually from https://github.com/${REPO}/releases" >&2
    exit 1 ;;
esac

# ── Detect arch ───────────────────────────────────────────────────────────────
ARCH="$(uname -m)"
case "${ARCH}" in
  x86_64|amd64)  ARCH="amd64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *)
    echo "error: unsupported architecture '${ARCH}'" >&2
    exit 1 ;;
esac

# ── Resolve latest version ────────────────────────────────────────────────────
echo "Fetching latest release..."

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
  # gh CLI path — works for private repos (internal users with org access)
  VERSION="$(gh release list --repo "${REPO}" --limit 1 --json tagName --jq '.[0].tagName')"
else
  # curl path — works once the repo is public
  VERSION="$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
    | grep '"tag_name"' | head -1 | cut -d'"' -f4)"
fi

if [ -z "${VERSION}" ]; then
  echo "error: could not determine latest version" >&2
  exit 1
fi
echo "Latest: ${VERSION}"

# ── Download and extract ──────────────────────────────────────────────────────
ARCHIVE="rubrik-rsc-plugin_${VERSION#v}_${OS}_${ARCH}.tar.gz"

echo "Downloading ${ARCHIVE}..."
if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
  gh release download "${VERSION}" --repo "${REPO}" \
    --pattern "${ARCHIVE}" --dir "${TMP}"
else
  URL="https://github.com/${REPO}/releases/download/${VERSION}/${ARCHIVE}"
  if command -v curl &>/dev/null; then
    curl -fsSL "${URL}" -o "${TMP}/${ARCHIVE}"
  elif command -v wget &>/dev/null; then
    wget -q "${URL}" -O "${TMP}/${ARCHIVE}"
  else
    echo "error: gh CLI, curl, or wget required" >&2
    exit 1
  fi
fi
tar -xzf "${TMP}/${ARCHIVE}" -C "${TMP}" "${BINARY}"

# ── Install ───────────────────────────────────────────────────────────────────
mkdir -p "${INSTALL_DIR}"
install -m 755 "${TMP}/${BINARY}" "${INSTALL_DIR}/${BINARY}"

echo ""
echo "✓ rubrik-mcp ${VERSION} installed to ${INSTALL_DIR}/${BINARY}"

# Warn if INSTALL_DIR is not on PATH
case ":${PATH}:" in
  *":${INSTALL_DIR}:"*) ;;
  *)
    echo ""
    echo "  Add to your PATH:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    ;;
esac

echo ""
echo "Next: configure your service account and AI platform"
echo "  Docs: https://rubrikinc.github.io/rubrik-mcp/getting-started"
