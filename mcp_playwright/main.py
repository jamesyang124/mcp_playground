"""
MCP Playwright Server
---------------------

This module provides AI/LLM-friendly tools for browser automation using Playwright, including:
- visit_page: Open a URL in a browser page.
- click_component: Click an HTML component by selector, with options for scrolling and navigation.
- enter_input: Enter text into an input field, optionally visiting a URL first.
- take_screenshot: Take a screenshot of the page or a specific element.

Intended for use in Model Context Protocol (MCP) servers and AI assistant environments.
"""

import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright


mcp = FastMCP("mcp_playwright")

# Singleton pattern for Playwright context
class PlaywrightSession:
    """
    Singleton class managing the Playwright browser, context, and page for
    browser automation tools. Ensures a single browser instance is reused
    across tool invocations, optimizing resource usage and session state.
    """
    _instance = None
    _playwright = None
    _browser = None
    _page = None

    @classmethod
    async def get_instance(cls, browser_agent="chromium"):
        """
        Initialize and return the singleton PlaywrightSession instance, launching the browser if
        necessary.
        Args:
            browser_agent (str): The browser to use (chromium, firefox, webkit). Defaults to
                "chromium".
        Returns:
            PlaywrightSession: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = PlaywrightSession()
            cls._playwright = await async_playwright().start()
            browser_launcher = getattr(cls._playwright, browser_agent)
            cls._browser = await browser_launcher.launch()
            cls._page = await cls._browser.new_page()
        return cls._instance

    @classmethod
    async def get_page(cls, browser_agent="chromium"):
        """
        Get the current Playwright page, launching a new one if needed.
        Args:
            browser_agent (str): The browser to use (chromium, firefox, webkit). Defaults to
                "chromium".
        Returns:
            Page: The Playwright page object.
        """
        await cls.get_instance(browser_agent)
        if cls._page is None or cls._page.is_closed():
            browser_launcher = getattr(cls._playwright, browser_agent)
            if cls._browser is None or cls._browser.is_closed():
                cls._browser = await browser_launcher.launch()
            cls._page = await cls._browser.new_page()
        return cls._page

    @classmethod
    async def close(cls):
        """
        Close the Playwright page, browser, and stop the Playwright instance, cleaning up resources.
        """
        if cls._page:
            await cls._page.close()
            cls._page = None
        if cls._browser:
            await cls._browser.close()
            cls._browser = None
        if cls._playwright:
            await cls._playwright.stop()
            cls._playwright = None
        cls._instance = None


@mcp.tool()
async def visit_page(url: str, browser_agent: str = "chromium"):
    """
    Visit the specified URL in a new browser page using Playwright.
    Args:
        url (str): The URL to visit.
        browser_agent (str, optional): The browser to use (chromium, firefox, webkit).
            Defaults to "chromium".
    """
    page = await PlaywrightSession.get_page(browser_agent)
    await page.goto(url)


@mcp.tool()
async def click_component(
    selector: str,
    scroll_into_view: bool = True,
    timeout: int = 5000,
    wait_for_navigation: bool = True
):
    """
    Click an HTML component specified by the selector, scrolling into view and waiting for
    visibility if needed. Optionally wait for navigation after click.
    Args:
        selector (str): The CSS selector of the component to click.
        scroll_into_view (bool): Whether to scroll the element into view before clicking.
            Defaults to True.
        timeout (int): Timeout in milliseconds to wait for the element to be visible.
            Defaults to 5000.
        wait_for_navigation (bool): Whether to wait for navigation after clicking.
            Defaults to True.
    """
    page = await PlaywrightSession.get_page()
    element = await page.query_selector(selector)
    if not element:
        raise RuntimeError(f"Element with selector '{selector}' not found.")
    if scroll_into_view:
        await element.scroll_into_view_if_needed(timeout=timeout)
    if wait_for_navigation:
        async with page.expect_navigation(timeout=timeout):
            await element.click(timeout=timeout)
    else:
        await element.click(timeout=timeout)


@mcp.tool()
async def enter_input(
    selector: str,
    text: str,
    browser_agent: str = "chromium"
):
    """
    Enter text into an input field specified by the selector.
    Args:
        selector (str): The CSS selector of the input field.
        text (str): The text to enter.
        browser_agent (str, optional): The browser to use (chromium, firefox, webkit).
            Defaults to "chromium".
    """
    page = await PlaywrightSession.get_page(browser_agent)
    await page.fill(selector, text)


@mcp.tool()
async def take_screenshot(
    selector: str = None,
    path: str = "screenshot.png"
):
    """
    Take a screenshot of the page or a specific element. Always appends a timestamp to the filename.
    Args:
        selector (str, optional): The CSS selector of the element to screenshot. Defaults to None
            (full page).
        path (str, optional): The base path for the screenshot file. Defaults to "screenshot.png".
    """
    page = await PlaywrightSession.get_page()
    screenshots_dir = os.environ.get("SCREENSHOTS_DIR", "./screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    base, ext = os.path.splitext(os.path.basename(path))
    timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
    filename = f"{base}{timestamp}{ext}"
    full_path = os.path.join(screenshots_dir, filename)
    if selector:
        element = await page.query_selector(selector)
        if element:
            await element.screenshot(path=full_path)
    else:
        await page.screenshot(path=full_path)


def main():
    """
    Entry point for the MCP Playwright server. Starts the server using
    standard I/O transport for communication with the MCP framework.
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
