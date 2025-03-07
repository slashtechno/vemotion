from dynaconf import Dynaconf, Validator
# import re

settings = Dynaconf(
    envvar_prefix="VEMOTION",
    load_dotenv=True,
    settings_files=["settings.toml", ".secrets.toml"],
    merge_enabled=True,
)
settings.validators.register(
    validators=[
        Validator(
            "slack_user_token",
            # must_exist=True,
            # condition=lambda x: x.startswith("xoxp-"),
            # messages={"condition": "Must start with 'xoxb-'"},
            default="",
        ),
        # Validator(
        #     "slack_app_token",
        #     must_exist=True,
        #     condition=lambda x: x.startswith("xapp-"),
        #     messages={"condition": "Must start with 'xapp-'"},
        # ),
            Validator(
            "status_prefix",
            default="",
        ),
        Validator(
            "db_path",
            default="db.json",
        ),
        Validator(
            "frontend_url",
            default="https://vemotion.angad.me",
        ),
        
    ],
)

settings.validators.validate()
