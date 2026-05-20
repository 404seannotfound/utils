#!/usr/bin/env python3
"""
build_seansheet.py — generate a self-contained setup-worksheet HTML from a JSON config.

The template (../assets/template.html) is the chassis: dark theme, progress bar,
sanity-checks panel, export panel, all the JS (validation, completion green-state,
copy buttons, action handlers, localStorage). It carries placeholders for the
project-specific bits.

The config describes:
  - project metadata (name, wordmark halves, paths, URLs)
  - a list of cards, each with optional links, instructions, and fields

This script stamps the cards into HTML and substitutes every placeholder.

Usage:
    python3 build_seansheet.py <config.json> <output.html>

Or, called as a module:
    from build_seansheet import build
    build(config_path, output_path)
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE_PATH = HERE.parent / "assets" / "template.html"


# ── Defaults so partial configs still work ────────────────────────────────

DEFAULT_LOGOMARK_SVG = '''<svg viewBox="0 0 64 64" width="42" height="42" aria-hidden="true">
  <defs><clipPath id="h"><circle cx="32" cy="34" r="26"/></clipPath></defs>
  <line x1="23" y1="8" x2="23" y2="14" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
  <circle cx="23" cy="6" r="2.6" fill="#FF6B58" stroke="#1A1A1A" stroke-width="1.2"/>
  <line x1="41" y1="8" x2="41" y2="14" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round"/>
  <circle cx="41" cy="6" r="2.6" fill="#5BA4E8" stroke="#1A1A1A" stroke-width="1.2"/>
  <g clip-path="url(#h)">
    <rect x="0" y="0" width="32" height="64" fill="#FF6B58"/>
    <rect x="32" y="0" width="32" height="64" fill="#5BA4E8"/>
  </g>
  <polygon points="22,25 28,38 16,38" fill="#F5F2EB" stroke="#1A1A1A" stroke-width="1.3"/>
  <circle cx="42" cy="33" r="6" fill="#F5F2EB" stroke="#1A1A1A" stroke-width="1.3"/>
  <circle cx="32" cy="34" r="26" fill="none" stroke="#1A1A1A" stroke-width="2.6"/>
  <line x1="32" y1="9" x2="32" y2="59" stroke="#1A1A1A" stroke-width="1.4"/>
</svg>'''

DEFAULT_PAGE_TITLE = "External credentials, gathered in one go."


# ── Card / field rendering ────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Turn 'Auth basics' into 'auth-basics' for data-card-id."""
    s = re.sub(r'[^a-z0-9]+', '-', text.lower())
    return s.strip('-') or 'card'


def _render_link(link: dict) -> str:
    label = html.escape(link['label'])
    url = html.escape(link['url'], quote=True)
    url_display = html.escape(link['url'])
    return (
        f'  <a class="go" href="{url}" target="_blank" rel="noopener">\n'
        f'    <span class="go__label">{label}</span>\n'
        f'    <span class="go__url">{url_display}</span>\n'
        f'  </a>\n'
    )


def _render_instructions(items: list) -> str:
    """Each item is either a string (HTML allowed) or {"html": "..."}. Renders to <ol>."""
    if not items:
        return ''
    lis = []
    for item in items:
        body = item if isinstance(item, str) else item.get('html', '')
        lis.append(f'    <li>{body}</li>')
    return '  <ol>\n' + '\n'.join(lis) + '\n  </ol>\n'


def _render_action(field_key: str, action: dict) -> str:
    """Render a per-field action button (Generate / Ping / Test OAuth flow)."""
    kind = action['kind']
    label = html.escape(action.get('label', kind))
    target = html.escape(field_key, quote=True)

    if kind == 'generate-hex' or kind == 'generate_hex':
        bytes_n = int(action.get('bytes', 32))
        return (
            f'      <button class="field__btn field__btn--accent" '
            f'data-action="generate-hex" data-target="{target}" '
            f'data-bytes="{bytes_n}">{label}</button>'
        )
    if kind == 'test-fetch' or kind == 'test_fetch':
        return (
            f'      <button class="field__btn" '
            f'data-action="test-fetch" data-target="{target}">{label}</button>'
        )
    if kind == 'test-github-oauth' or kind == 'test_github_oauth':
        return (
            f'      <button class="field__btn" '
            f'data-action="test-github-oauth" data-target="{target}">{label}</button>'
        )
    # Unknown kind: silently render nothing rather than break the worksheet.
    return ''


def _render_field(field: dict) -> str:
    key = field['key']
    key_esc = html.escape(key, quote=True)
    required = field.get('required', True)
    secret = field.get('secret', False)  # password input vs text
    optional_attr = ' data-optional' if not required else ''
    type_attr = 'password' if secret else 'text'
    placeholder = html.escape(field.get('placeholder', ''), quote=True)
    default = html.escape(field.get('default', ''), quote=True)
    validate = html.escape(field.get('validate', ''), quote=True)
    hint = field.get('hint', '')
    actions = field.get('actions', [])

    # Required asterisk in the label
    req_marker = '<span class="req">*</span>' if required else ''

    # value="..." vs placeholder
    value_attr = f' value="{default}"' if default else ''
    placeholder_attr = f' placeholder="{placeholder}"' if placeholder else ''
    validate_attr = f' data-validate="{validate}"' if validate else ''

    input_html = (
        f'      <input class="field__input" type="{type_attr}"'
        f'{value_attr}{placeholder_attr} autocomplete="off" spellcheck="false"'
        f'{validate_attr}>'
    )

    action_buttons = '\n'.join(_render_action(key, a) for a in actions if a)
    action_block = ('\n' + action_buttons) if action_buttons else ''

    # Show the test-result slot only if at least one of the actions writes to it.
    has_test_result = any(
        a['kind'].replace('_', '-') in ('test-fetch', 'test-github-oauth')
        for a in actions
    )
    test_result_html = (
        f'    <div class="field__test-result" data-test-result="{key_esc}"></div>\n'
        if has_test_result else ''
    )

    hint_html = f'    <div class="field__hint">{hint}</div>\n' if hint else ''

    return (
        f'  <div class="field" data-secret="{key_esc}"{optional_attr}>\n'
        f'    <label class="field__label">{html.escape(key)}{req_marker}</label>\n'
        f'    <div class="field__row">\n'
        f'{input_html}{action_block}\n'
        f'    </div>\n'
        f'{test_result_html}'
        f'{hint_html}'
        f'  </div>\n'
    )


def _render_card(card: dict, index: int) -> str:
    """One <section class='card'> per item in config['cards']."""
    card_id = card.get('id') or _slugify(card['title'])
    step = card.get('step') or f'Step {index + 1}'
    title = html.escape(card['title'])
    subtitle = card.get('subtitle', '')

    links_html = ''.join(_render_link(l) for l in card.get('links', []))
    instructions_html = _render_instructions(card.get('instructions', []))
    fields_html = ''.join(_render_field(f) for f in card.get('fields', []))

    subtitle_html = f'  <p class="card__sub">{subtitle}</p>\n' if subtitle else ''

    return (
        f'<section class="card" data-card-id="{html.escape(card_id, quote=True)}">\n'
        f'  <div class="card__head">\n'
        f'    <span class="card__num">{html.escape(step)}</span>\n'
        f'    <h2 class="card__title">{title}</h2>\n'
        f'  </div>\n'
        f'{subtitle_html}'
        f'{links_html}'
        f'{instructions_html}'
        f'{fields_html}'
        f'</section>\n\n'
    )


# ── Top-level build ───────────────────────────────────────────────────────

def build(config_path: Path, output_path: Path) -> None:
    config = json.loads(Path(config_path).read_text())
    project = config.get('project', {})

    cards_html = ''.join(_render_card(c, i) for i, c in enumerate(config.get('cards', [])))

    substitutions = {
        '{{TITLE}}': project.get('title') or f"{project.get('name', 'project')} — setup worksheet",
        '{{PREVIEW_URL}}': project.get('preview_url') or '#',
        '{{LOGOMARK_SVG}}': project.get('logomark_svg') or DEFAULT_LOGOMARK_SVG,
        '{{WORDMARK_LEFT}}': project.get('wordmark_left') or project.get('name', 'set'),
        '{{WORDMARK_RIGHT}}': project.get('wordmark_right') or 'up',
        '{{SUBTITLE}}': project.get('subtitle') or 'setup worksheet',
        '{{PAGE_TITLE}}': project.get('page_title') or DEFAULT_PAGE_TITLE,
        '{{STORAGE_KEY}}': project.get('storage_key') or f"{project.get('name', 'sheet')}-setup",
        '{{WRANGLER_PROJECT}}': project.get('wrangler_project') or project.get('name', ''),
        '{{VSCODE_DEV_VARS_PATH}}': project.get('dev_vars_path') or '/tmp/.dev.vars',
        '{{REPO_PATH}}': project.get('repo_path') or '~/your-repo/',
        '{{CARDS_HTML}}': cards_html,
    }

    template = TEMPLATE_PATH.read_text()
    out = template
    for placeholder, value in substitutions.items():
        out = out.replace(placeholder, value)

    # Sanity check: any unsubstituted placeholders left?
    leftover = re.findall(r'\{\{[A-Z_]+\}\}', out)
    if leftover:
        sys.stderr.write(
            f"WARNING: unsubstituted placeholders in output: {sorted(set(leftover))}\n"
        )

    Path(output_path).write_text(out)
    print(f"wrote {output_path} ({len(out):,} bytes, {out.count(chr(10)):,} lines)")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    build(Path(argv[1]), Path(argv[2]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
