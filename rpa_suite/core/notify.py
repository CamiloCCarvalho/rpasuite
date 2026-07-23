# rpa_suite/core/notify.py

# imports standard
from typing import Any, Dict, Optional

# imports third-party
import requests


class NotifierError(Exception):
    """Custom exception for Notifier errors."""

    def __init__(self, message: str) -> None:
        clean_message = message.replace("NotifierError:", "").strip()
        super().__init__(f"NotifierError: {clean_message}")


class Notifier:
    """
    Simple HTTP-webhook notification helper.

    Provides a generic `send_webhook(url, payload)` plus opinionated helpers
    for popular chat services (`slack`, `teams`, `telegram`). Uses `requests`,
    which is already a dependency of the suite.

    Example:
        >>> from rpa_suite.core.notify import Notifier
        >>> n = Notifier()
        >>> n.slack("https://hooks.slack.com/...", "Robot finished with 42 items")
    """

    default_timeout: float = 15.0

    def __init__(self, default_timeout: float = 15.0) -> None:
        """
        Args:
            default_timeout: Default request timeout (in seconds) applied to
                every webhook call unless overridden per-call.
        """
        if default_timeout <= 0:
            raise NotifierError("`default_timeout` must be > 0")
        self.default_timeout = default_timeout

    def send_webhook(
        self,
        url: str,
        payload: Dict[str, Any],
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Send a JSON payload to `url` via HTTP.

        Parameters:
        ----------
        url : str
            Full webhook URL.
        payload : dict
            JSON-serializable payload.
        method : str
            HTTP method (default "POST").
        headers : dict, optional
            Extra HTTP headers (merged over the default `Content-Type: application/json`).
        timeout : float, optional
            Per-call timeout. Falls back to `self.default_timeout`.

        Returns:
        ----------
        dict with:
            * 'status_code' : HTTP status code
            * 'ok'          : True when 2xx
            * 'body'        : raw response text (truncated implicitly by server)

        Raises:
        ----------
        NotifierError: on network errors or when the URL is empty.
        """
        if not url:
            raise NotifierError("`url` cannot be empty")

        merged_headers = {"Content-Type": "application/json"}
        if headers:
            merged_headers.update(headers)

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                json=payload,
                headers=merged_headers,
                timeout=timeout or self.default_timeout,
            )
            return {
                "status_code": response.status_code,
                "ok": response.ok,
                "body": response.text,
            }
        except requests.RequestException as e:
            raise NotifierError(f"Webhook request failed: {str(e)}") from e

    def slack(
        self,
        webhook_url: str,
        text: str,
        blocks: Optional[list] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to a Slack Incoming Webhook.

        Parameters:
        ----------
        webhook_url : str
            Slack Incoming Webhook URL.
        text : str
            Message text. Used as fallback when `blocks` is provided.
        blocks : list, optional
            Slack "blocks" payload for rich formatting.
        timeout : float, optional
            Per-call timeout.
        """
        payload: Dict[str, Any] = {"text": text}
        if blocks:
            payload["blocks"] = blocks
        return self.send_webhook(webhook_url, payload, timeout=timeout)

    def teams(
        self,
        webhook_url: str,
        title: str,
        text: str,
        theme_color: str = "0076D7",
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Send a MessageCard to a Microsoft Teams Incoming Webhook.

        Uses the legacy MessageCard format (still supported by Teams
        Incoming Webhooks) with a colored theme.
        """
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": theme_color,
            "title": title,
            "text": text,
        }
        return self.send_webhook(webhook_url, payload, timeout=timeout)

    def telegram(
        self,
        bot_token: str,
        chat_id: str | int,
        text: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = True,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Send a message via the Telegram Bot API `sendMessage` endpoint.

        Parameters:
        ----------
        bot_token : str
            Telegram bot token (from `@BotFather`).
        chat_id : str | int
            Target chat id or `@channelusername`.
        text : str
            Message text.
        parse_mode : str, optional
            "Markdown", "MarkdownV2" or "HTML" — see Telegram docs.
        disable_web_page_preview : bool
            Whether to suppress link previews (default True).
        timeout : float, optional
            Per-call timeout.
        """
        if not bot_token:
            raise NotifierError("`bot_token` cannot be empty")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        return self.send_webhook(url, payload, timeout=timeout)
