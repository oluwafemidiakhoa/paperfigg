from __future__ import annotations

import asyncio
import importlib
import json
import os
import shlex
import uuid
from typing import Any, Dict, List, Optional, Tuple


class PythonSDKMCPClient:
    """
    Optional MCP transport using the official Python SDK over stdio.
    This is only activated when PAPERFIG_MCP_COMMAND is configured.
    """

    def __init__(self, command: str, args: Optional[List[str]] = None) -> None:
        self.command = command
        self.args = args or []

    def call_tool(self, server: Optional[str], tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # `server` is ignored for direct stdio transport; included for API compatibility.
        del server
        return asyncio.run(self._call_tool(tool=tool, arguments=arguments))

    async def _call_tool(self, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from mcp import ClientSession, StdioServerParameters  # type: ignore
            from mcp.client.stdio import stdio_client  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "MCP SDK not installed. Install optional dependency `mcp`."
            ) from exc

        params = StdioServerParameters(command=self.command, args=self.args)
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments)
        return _normalize_mcp_response(result)


def _normalize_mcp_response(result: Any) -> Dict[str, Any]:
    if isinstance(result, dict):
        payload = result
    elif hasattr(result, "model_dump"):
        payload = result.model_dump()  # type: ignore[assignment]
    elif hasattr(result, "dict"):
        payload = result.dict()  # type: ignore[assignment]
    else:
        payload = {}

    if isinstance(payload.get("svg"), str):
        return payload

    for container_key in ("result", "data", "output"):
        candidate = payload.get(container_key)
        if isinstance(candidate, dict) and isinstance(candidate.get("svg"), str):
            return candidate

    structured = payload.get("structuredContent")
    if isinstance(structured, dict):
        return structured

    text_chunks: List[str] = []
    content_items = payload.get("content", [])
    for item in content_items:
        if isinstance(item, dict):
            text_value = item.get("text")
        else:
            text_value = getattr(item, "text", None)
        if isinstance(text_value, str):
            text_chunks.append(text_value)

    for chunk in text_chunks:
        try:
            parsed = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    raise RuntimeError("MCP tool response did not include parseable structured content.")


def _load_client_factory(factory_spec: str) -> Any:
    if ":" not in factory_spec:
        raise RuntimeError(
            "Invalid PAPERFIG_MCP_CLIENT_FACTORY format. Use 'module_path:factory_name'."
        )
    module_name, symbol = factory_spec.split(":", 1)
    module = importlib.import_module(module_name)
    target = getattr(module, symbol)
    client = target() if callable(target) else target
    if not hasattr(client, "call_tool"):
        raise RuntimeError("Loaded MCP client does not implement call_tool(server, tool, arguments).")
    return client


class PaperBananaClient:
    """
    Minimal MCP wrapper for PaperBanana. This class does not reimplement
    PaperBanana; it delegates to an MCP server tool call.
    """

    def __init__(self, mcp_client: Optional[Any] = None, server: Optional[str] = None) -> None:
        self.server = server or os.getenv("PAPERFIG_MCP_SERVER")
        self.mock_mode = os.getenv("PAPERFIG_MOCK_PAPERBANANA", "0") == "1"
        self.mcp_client = mcp_client or self._resolve_mcp_client()

    def generate_svg(self, spec: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        if self.mock_mode:
            return self._mock_svg(spec)

        if not self.server or not self.mcp_client:
            raise RuntimeError(
                "PaperBanana MCP is not configured. Set PAPERFIG_MCP_SERVER and either "
                "PAPERFIG_MCP_CLIENT_FACTORY or PAPERFIG_MCP_COMMAND, or enable PAPERFIG_MOCK_PAPERBANANA=1."
            )

        # Expected MCP tool signature: paperbanana.generate
        response = self.mcp_client.call_tool(
            server=self.server,
            tool="paperbanana.generate",
            arguments=spec,
        )
        svg = response.get("svg")
        elements = response.get("elements", [])
        if not svg:
            raise RuntimeError("PaperBanana MCP did not return SVG output.")
        return svg, elements

    def _resolve_mcp_client(self) -> Optional[Any]:
        factory = os.getenv("PAPERFIG_MCP_CLIENT_FACTORY")
        if factory:
            return _load_client_factory(factory)

        command = os.getenv("PAPERFIG_MCP_COMMAND")
        if command:
            args = shlex.split(os.getenv("PAPERFIG_MCP_ARGS", ""))
            return PythonSDKMCPClient(command=command, args=args)

        return None

    def _mock_svg(self, spec: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        figure_id = spec.get("figure_id") or f"fig-{uuid.uuid4().hex[:8]}"
        title = spec.get("title", "Figure")
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='800' height='450' viewBox='0 0 800 450'>"
            "<rect x='40' y='40' width='720' height='370' fill='white' stroke='black'/>"
            f"<text x='60' y='90' font-family='Times New Roman' font-size='24'>{title}</text>"
            "<line x1='60' y1='120' x2='740' y2='120' stroke='black'/>"
            "<text x='60' y='170' font-family='Times New Roman' font-size='16'>Mock PaperBanana output</text>"
            "</svg>"
        )
        elements = [
            {
                "id": f"{figure_id}-title",
                "type": "text",
                "label": title,
                "source_spans": spec.get("source_spans", []),
            }
        ]
        return svg, elements
