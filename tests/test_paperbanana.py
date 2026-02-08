from __future__ import annotations

import os
import sys
import types
import unittest
from unittest.mock import patch

from paperfig.utils.paperbanana import (
    PaperBananaClient,
    PythonSDKMCPClient,
    _normalize_mcp_response,
)


class _FakeMCPClient:
    def __init__(self) -> None:
        self.calls = []

    def call_tool(self, server, tool, arguments):
        self.calls.append({"server": server, "tool": tool, "arguments": arguments})
        return {
            "svg": "<svg><text>ok</text></svg>",
            "elements": [
                {
                    "id": "e1",
                    "type": "text",
                    "label": "ok",
                    "source_spans": [
                        {
                            "section": "methodology",
                            "start": 1,
                            "end": 5,
                            "quote": "test",
                        }
                    ],
                }
            ],
        }


class PaperBananaClientTests(unittest.TestCase):
    def test_mock_mode_generates_svg_and_elements(self) -> None:
        with patch.dict(os.environ, {"PAPERFIG_MOCK_PAPERBANANA": "1"}, clear=False):
            client = PaperBananaClient()
            svg, elements = client.generate_svg({"figure_id": "fig-a", "title": "A"})

        self.assertIn("<svg", svg)
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]["id"], "fig-a-title")

    def test_configured_client_is_used_for_tool_call(self) -> None:
        fake = _FakeMCPClient()
        with patch.dict(os.environ, {"PAPERFIG_MOCK_PAPERBANANA": "0"}, clear=False):
            client = PaperBananaClient(mcp_client=fake, server="paperbanana-server")
            svg, elements = client.generate_svg({"figure_id": "fig-b"})

        self.assertEqual(svg, "<svg><text>ok</text></svg>")
        self.assertEqual(len(elements), 1)
        self.assertEqual(len(fake.calls), 1)
        self.assertEqual(fake.calls[0]["server"], "paperbanana-server")
        self.assertEqual(fake.calls[0]["tool"], "paperbanana.generate")

    def test_missing_configuration_raises(self) -> None:
        with patch.dict(
            os.environ,
            {
                "PAPERFIG_MOCK_PAPERBANANA": "0",
                "PAPERFIG_MCP_SERVER": "",
                "PAPERFIG_MCP_CLIENT_FACTORY": "",
                "PAPERFIG_MCP_COMMAND": "",
            },
            clear=False,
        ):
            client = PaperBananaClient()
            with self.assertRaises(RuntimeError):
                client.generate_svg({"figure_id": "fig-c"})

    def test_factory_loader_from_environment(self) -> None:
        module_name = "paperfig_test_fake_factory"
        module = types.ModuleType(module_name)

        def _factory():
            return _FakeMCPClient()

        module.build = _factory
        sys.modules[module_name] = module
        try:
            with patch.dict(
                os.environ,
                {
                    "PAPERFIG_MOCK_PAPERBANANA": "0",
                    "PAPERFIG_MCP_SERVER": "srv",
                    "PAPERFIG_MCP_CLIENT_FACTORY": f"{module_name}:build",
                    "PAPERFIG_MCP_COMMAND": "",
                },
                clear=False,
            ):
                client = PaperBananaClient()
                self.assertIsNotNone(client.mcp_client)
                svg, _ = client.generate_svg({"figure_id": "fig-d"})
                self.assertIn("<svg", svg)
        finally:
            del sys.modules[module_name]

    def test_command_configuration_creates_sdk_client(self) -> None:
        with patch.dict(
            os.environ,
            {
                "PAPERFIG_MOCK_PAPERBANANA": "0",
                "PAPERFIG_MCP_SERVER": "srv",
                "PAPERFIG_MCP_CLIENT_FACTORY": "",
                "PAPERFIG_MCP_COMMAND": "paperbanana-mcp",
                "PAPERFIG_MCP_ARGS": "--transport stdio",
            },
            clear=False,
        ):
            client = PaperBananaClient()

        self.assertIsInstance(client.mcp_client, PythonSDKMCPClient)
        self.assertEqual(client.mcp_client.command, "paperbanana-mcp")
        self.assertEqual(client.mcp_client.args, ["--transport", "stdio"])

    def test_normalize_accepts_root_svg_payload(self) -> None:
        payload = {"svg": "<svg/>", "elements": []}
        normalized = _normalize_mcp_response(payload)
        self.assertEqual(normalized["svg"], "<svg/>")

    def test_normalize_accepts_nested_result_payload(self) -> None:
        payload = {"result": {"svg": "<svg/>", "elements": []}}
        normalized = _normalize_mcp_response(payload)
        self.assertEqual(normalized["svg"], "<svg/>")


if __name__ == "__main__":
    unittest.main()
