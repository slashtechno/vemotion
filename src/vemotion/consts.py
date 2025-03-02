from vemotion import settings
SLACK_OAUTH_REDIRECT_URI = "https://vemotion.angad.me/api/oauth/callback"

SLACK_OAUTH_AUTHORIZE_URL = "https://slack.com/oauth/v2/authorize"
SLACK_OAUTH_ACCESS_URL = "https://slack.com/api/oauth.v2.access"
URL = (
    f"{SLACK_OAUTH_AUTHORIZE_URL}?client_id={settings.slack_client_id}"
    f"&scope=users:read,chat:write"
    f"&redirect_uri={SLACK_OAUTH_REDIRECT_URI}"
)