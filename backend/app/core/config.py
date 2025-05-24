import secrets
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


# 类属性名全大写会直接映射环境变量
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # API端点前缀
    API_V1_STR: str = "/api/v1"

    # 随机生成的加密密钥
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # 访问令牌过期时间（单位：分钟）
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # 前端主机地址
    FRONTEND_HOST: str = "http://localhost:5173"

    # 环境
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # CORS白名单
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    # 动态计算的模型字段
    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        # 移除末尾斜杠，避免http://site.com和http://site.com/被识别为不同来源
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # 项目名称
    PROJECT_NAME: str

    # PostgreSQL数据库配置
    # 数据库服务器地址
    POSTGRES_SERVER: str
    # 数据库端口
    POSTGRES_PORT: int = 5432
    # 数据库用户名
    POSTGRES_USER: str
    # 数据库密码
    POSTGRES_PASSWORD: str = ""
    # 使用的DB名称
    POSTGRES_DB: str = ""

    # 生成SQLAlchemy数据库连接URI
    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # 邮件服务器配置
    # TLS加密
    SMTP_TLS: bool = True
    # SSL加密
    SMTP_SSL: bool = False
    # 邮件服务端口
    SMTP_PORT: int = 587
    # SMTP服务器地址
    SMTP_HOST: str | None = None
    # SMTP服务器用户名
    SMTP_USER: str | None = None
    # SMTP服务器密码
    SMTP_PASSWORD: str | None = None
    # 邮件发送者邮箱
    EMAILS_FROM_EMAIL: EmailStr | None = None
    # 邮件发送者名称
    EMAILS_FROM_NAME: EmailStr | None = None

    # 模型验证，在模型实例化后执行的验证逻辑
    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    # 密码重置邮件的有效期设置（单位：小时）
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # 邮件发送是否启用
    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # 测试邮箱和超级用户配置
    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str


settings = Settings()  # type: ignore
