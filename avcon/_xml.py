"""XML request builder and response parser for DENON AVR API."""

from __future__ import annotations

import xml.etree.ElementTree as ET


def build_simple_cmd(*commands: str) -> str:
    """Build AppCommand.xml format request body.

    Max 5 commands per request (API limitation).
    """
    if len(commands) > 5:
        raise ValueError("AppCommand.xml は最大5コマンドまで")
    lines = ['<?xml version="1.0" encoding="utf-8" ?>', "<tx>"]
    for i, cmd in enumerate(commands, 1):
        lines.append(f'<cmd id="{i}">{cmd}</cmd>')
    lines.append("</tx>")
    return "\n".join(lines)


def build_param_cmd(name: str, params: list[str]) -> str:
    """Build AppCommand0300.xml format request body.

    Newlines in XML are required -- single-line XML returns empty response.
    """
    lines = [
        '<?xml version="1.0" encoding="utf-8" ?>',
        "<tx>",
        '<cmd id="3">',
        f"<name>{name}</name>",
    ]
    if params:
        lines.append("<list>")
        for p in params:
            lines.append(f'<param name="{p}" />')
        lines.append("</list>")
    else:
        lines.append("<list />")
    lines.extend(["</cmd>", "</tx>"])
    return "\n".join(lines)


def parse_params(root: ET.Element) -> dict[str, tuple[str, int]]:
    """Parse 0300 response params into {name: (value, control)}.

    Values are automatically stripped of padding.
    """
    result: dict[str, tuple[str, int]] = {}
    for param in root.findall(".//list/param"):
        name = param.get("name", "")
        control = int(param.get("control", "0"))
        value = (param.text or "").strip()
        if name:
            result[name] = (value, control)
    return result
