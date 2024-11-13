from __future__ import annotations

import asyncio
from importlib.metadata import version

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.demo.page import PageScreen
from textual.reactive import reactive
from textual.widgets import Collapsible, Digits, Footer, Label, Markdown

WHAT_IS_TEXTUAL_MD = """\
# What is Textual?

Snappy, keyboard-centric, applications that run in the terminal and [the web](https://github.com/Textualize/textual-web).

🐍 All you need is Python!

"""

WELCOME_MD = """\
## Welcome keyboard warriors!

This is a Textual app. Here's what you need to know:

* **enter** `toggle this collapsible widget`
* **tab** `focus the next widget`
* **shift+tab** `focus the previous widget`
* **ctrl+p** `summon the command palette`


👇 Also see the footer below.

`Or… click away with the mouse (no judgement).`

"""

ABOUT_MD = """\
The retro look is not just an aesthetic choice! Textual apps have some unique properties that make them preferable for many tasks.

## Textual interfaces are *snappy*
Even the most modern of web apps can leave the user waiting hundreds of milliseconds or more for a response.
Given their low graphical requirements, Textual interfaces can be far more responsive — no waiting required.

## Reward repeated use
Use the mouse to explore, but Textual apps are keyboard-centric and reward repeated use.
An experienced user can operate a Textual app far faster than their web / GUI counterparts.

## Command palette
A builtin command palette with fuzzy searching puts powerful commands at your fingertips.

**Try it:** Press **ctrl+p** now.

"""

API_MD = """\
A modern Python API from the developer of [Rich](https://github.com/Textualize/rich).

```python
# Start building!
import textual
```

Well documented, typed, and intuitive.
Textual's API is accessible to Python developers of all skill levels.

**Hint:** press **C** to view the code for this page.

## Built on Rich

With over 1.5 *billion* downloads, Rich is the most popular terminal library out there.
Textual builds on Rich to add interactivity, and is compatible with Rich renderables.

## Re-usable widgets

Textual's widgets are self-contained and re-usable across projects.
Virtually all aspects of a widget's look and feel can be customized to your requirements.

## Builtin widgets

A large [library of builtin widgets](https://textual.textualize.io/widget_gallery/), and a growing ecosystem of third party widgets on PyPI
(this content is generated by the builtin [Markdown](https://textual.textualize.io/widget_gallery/#markdown) widget).
    
## Reactive variables

[Reactivity](https://textual.textualize.io/guide/reactivity/) using Python idioms, keeps your logic separate from display code.

## Async support

Built on asyncio, you can easily integrate async libraries while keeping your UI responsive.

## Concurrency

Textual's [Workers](https://textual.textualize.io/guide/workers/) provide a far-less error prone interface to
concurrency: both async and threads.

## Testing

With a comprehensive [testing framework](https://textual.textualize.io/guide/testing/), you can release reliable software, that can be maintained indefinitely.

## Docs

Textual has [amazing docs](https://textual.textualize.io/)!

"""

DEPLOY_MD = """\
There are a number of ways to deploy and share Textual apps.

## As a Python library

Textual apps may be pip installed, via tools such as `pipx` or `uvx`, and other package managers.

## As a web application

It takes two lines of code to [serve your Textual app](https://github.com/Textualize/textual-serve) as a web application.

## Managed web application

With [Textual web](https://github.com/Textualize/textual-web) you can serve multiple Textual apps on the web,
with zero configuration. Even behind a firewall.
"""


class StarCount(Vertical):
    """Widget to get and display GitHub star count."""

    DEFAULT_CSS = """
    StarCount {
        dock: top;
        height: 6;
        border-bottom: hkey $background;
        border-top: hkey $background;
        layout: horizontal;
        background: $boost;
        padding: 0 1;
        color: $text-warning;
        #stars { align: center top; }
        #forks { align: right top; }
        Label { text-style: bold; }
        LoadingIndicator { background: transparent !important; }
        Digits { width: auto; margin-right: 1; }
        Label { margin-right: 1; }
        align: center top;
        &>Horizontal { max-width: 100;} 
    }
    """
    stars = reactive(25251, recompose=True)
    forks = reactive(776, recompose=True)

    @work
    async def get_stars(self):
        """Worker to get stars from GitHub API."""
        if not HTTPX_AVAILABLE:
            self.notify(
                "Install httpx to update stars from the GitHub API.\n\n$ [b]pip install httpx[/b]",
                title="GitHub Stars",
            )
            return
        self.loading = True
        try:
            await asyncio.sleep(1)  # Time to admire the loading indicator
            async with httpx.AsyncClient() as client:
                repository_json = (
                    await client.get("https://api.github.com/repos/textualize/textual")
                ).json()
            self.stars = repository_json["stargazers_count"]
            self.forks = repository_json["forks"]
        except Exception:
            self.notify(
                "Unable to update star count (maybe rate-limited)",
                title="GitHub stars",
                severity="error",
            )
        self.loading = False

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="version"):
                yield Label("Version")
                yield Digits(version("textual"))
            with Vertical(id="stars"):
                yield Label("GitHub ★")
                stars = f"{self.stars / 1000:.1f}K"
                yield Digits(stars).with_tooltip(f"{self.stars} GitHub stars")
            with Vertical(id="forks"):
                yield Label("Forks")
                yield Digits(str(self.forks)).with_tooltip(f"{self.forks} Forks")

    def on_mount(self) -> None:
        self.tooltip = "Click to refresh"
        self.get_stars()

    def on_click(self) -> None:
        self.get_stars()


class Content(VerticalScroll, can_focus=False):
    """Non focusable vertical scroll."""


class HomeScreen(PageScreen):
    DEFAULT_CSS = """
    HomeScreen {
        
        Content {
            align-horizontal: center;
            & > * {
                max-width: 100;
            }      
            margin: 0 1;          
            overflow-y: auto;
            height: 1fr;
            scrollbar-gutter: stable;
            MarkdownFence {
                height: auto;
                max-height: initial;
            }
            Collapsible {
                padding-right: 0;               
                &.-collapsed { padding-bottom: 1; }
            }
            Markdown {
                margin-right: 1;
                padding-right: 1;
                background: transparent;
            }
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield StarCount()
        with Content():
            yield Markdown(WHAT_IS_TEXTUAL_MD)
            with Collapsible(title="Welcome", collapsed=False):
                yield Markdown(WELCOME_MD)
            with Collapsible(title="Textual Interfaces"):
                yield Markdown(ABOUT_MD)
            with Collapsible(title="Textual API"):
                yield Markdown(API_MD)
            with Collapsible(title="Deploying Textual apps"):
                yield Markdown(DEPLOY_MD)
        yield Footer()
