from pathlib import Path
import sys
from typing import ClassVar

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class Group(BaseModel):
    name: str
    type: str
    rule: bool = True
    manual: bool = False
    prior: str | None = None
    regex: str | None = None


class Config(BaseSettings):
    HEAD: dict[str, object] = Field(default_factory=dict)
    TEST_URL: str = "http://www.gstatic.com/generate_204"
    RULESET: list[tuple[str, str]] = Field(default_factory=list)
    CUSTOM_PROXY_GROUP: list[Group] = Field(default_factory=list)

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        yaml_file="config.yaml"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


try:
    if Path("config.yaml").exists():
        with open("config.yaml", "r", encoding="utf-8") as f:
            if f.read() == "":
                raise FileNotFoundError
    configInstance = Config()
except FileNotFoundError:
    print(
        f"config.yaml not found or empty, please run {sys.argv[0]} -h to see how to generate a default config file"
    )
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
