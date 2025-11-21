# -*- coding: utf-8 -*-
"""ÐÐ°ÐÐ¾ÑÐ° Ñ ÐÐ°Ð·Ð¾Ð¹ Ð´Ð°Ð½Ð½ÑÑ"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from .models import Base
from config import settings
import os
import logging

logger = logging.getLogger(__name__)

# ÐÐµÐ½ÐÐ²Ð°Ñ ÐÐ½ÐÑÐÐ°Ð»ÐÐ·Ð°ÑÐÑ Ð´Ð²ÐÐ¶ÐºÐ° ÐÐ°Ð·Ñ Ð´Ð°Ð½Ð½ÑÑ
_engine = None
_AsyncSessionLocal = None

def _init_engine():
    """ÐÐ½ÐÑÐÐ°Ð»ÐÐ·ÐÑÐ¾Ð²Ð°ÑÑ Ð´Ð²ÐÐ¶Ð¾Ðº ÐÐ°Ð·Ñ Ð´Ð°Ð½Ð½ÑÑ"""
    global _engine, _AsyncSessionLocal
    
    if _engine is not None:
        return  # Ð£Ð¶Ðµ ÐÐ½ÐÑÐÐ°Ð»ÐÐ·ÐÑÐ¾Ð²Ð°Ð½
    
    if not settings.DATABASE_URL:
        logger.warning(
            "DATABASE_URL not set. Database operations will fail. "
            "Please set DATABASE_URL environment variable. "
            "For Yandex Cloud, use PostgreSQL: postgresql+asyncpg://user:password@rc1a-xxx.mdb.yandexcloud.net:6432/dbname?ssl=require"
        )
        # ÐÐ¾Ð·Ð´Ð°ÐµÐ¼ Ð·Ð°ÐÐ»ÑÑÐºÑ ÑÑÐ¾ÐÑ Ð½Ðµ Ð¿Ð°Ð´Ð°ÑÑ Ð¿ÑÐ ÐÐ¼Ð¿Ð¾ÑÑÐµ
        return
    
    # ÐÐ²ÑÐ¾Ð¼Ð°ÑÐÑÐµÑÐºÐ¾Ðµ Ð¿ÑÐµÐ¾ÐÑÐ°Ð·Ð¾Ð²Ð°Ð½ÐÐµ ÑÑÐ°Ð½Ð´Ð°ÑÑÐ½Ð¾ÐÐ¾ PostgreSQL URL Ð´Ð»Ñ asyncpg
    database_url = settings.DATABASE_URL
    ssl_required = False
    
    # ÐÑÐ¾Ð²ÐµÑÑÐµÐ¼ Ð½Ð°Ð»ÐÑÐÐµ sslmode=require Ð² URL
    if "sslmode=require" in database_url or "ssl=require" in database_url:
        ssl_required = True
        # Ð£ÐÐÑÐ°ÐµÐ¼ Ð¿Ð°ÑÐ°Ð¼ÐµÑÑ sslmode ÐÐ· URL (asyncpg Ð½Ðµ Ð¿Ð¾Ð´Ð´ÐµÑÐ¶ÐÐ²Ð°ÐµÑ ÐµÐÐ¾ Ð² URL)
        database_url = database_url.replace("?sslmode=require", "").replace("&sslmode=require", "")
        database_url = database_url.replace("?ssl=require", "").replace("&ssl=require", "")
    
    if database_url.startswith("postgresql://") and not database_url.startswith("postgresql+asyncpg://"):
        # ÐÑÐµÐ¾ÐÑÐ°Ð·ÑÐµÐ¼ ÑÑÐ°Ð½Ð´Ð°ÑÑÐ½ÑÐ¹ PostgreSQL URL Ð´Ð»Ñ asyncpg
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        logger.info("Converted PostgreSQL URL to asyncpg format for Yandex Cloud compatibility")
    
    # ÐÐ°ÑÑÑÐ¾Ð¹ÐºÐ° SSL Ð´Ð»Ñ Yandex Cloud Ð Ð´ÑÑÐÐÑ Ð¿ÑÐ¾Ð²Ð°Ð¹Ð´ÐµÑÐ¾Ð², ÑÑÐµÐÑÑÑÐÑ SSL
    connect_args = {}
    if ssl_required:
        import ssl
        # Yandex Cloud использует самоподписанный сертификат, поэтому отключаем проверку
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_context
        logger.info("SSL enabled for database connection (Yandex Cloud, self-signed cert)")
    
    try:
        _engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            connect_args=connect_args if connect_args else {}
        )
        
        _AsyncSessionLocal = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("Database engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database engine: {e}")
        raise

# ÐÐ½ÐÑÐÐ°Ð»ÐÐ·ÐÑÑÐµÐ¼ Ð¿ÑÐ ÐÐ¼Ð¿Ð¾ÑÑÐµ Ð¼Ð¾Ð´ÑÐ»Ñ (Ð½Ð¾ ÑÐ¾Ð»ÑÐºÐ¾ ÐµÑÐ»Ð DATABASE_URL ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½)
_init_engine()

# ÐÐ»Ñ Ð¾ÐÑÐ°ÑÐ½Ð¾Ð¹ ÑÐ¾Ð²Ð¼ÐµÑÑÐÐ¼Ð¾ÑÑÐ - ÐÑÐ¿Ð¾Ð»ÑÐ·ÑÐµÐ¼ ÑÑÐ½ÐºÑÐÐ Ð²Ð¼ÐµÑÑÐ¾ Ð¿ÑÑÐ¼Ð¾ÐÐ¾ Ð´Ð¾ÑÑÑÐ¿Ð°
def get_engine():
    """ÐÐ¾Ð»ÑÑÐÑÑ Ð´Ð²ÐÐ¶Ð¾Ðº ÐÐ°Ð·Ñ Ð´Ð°Ð½Ð½ÑÑ"""
    _init_engine()
    if _engine is None:
        raise ValueError("DATABASE_URL not set. Cannot initialize database engine.")
    return _engine

def get_session_factory():
    """ÐÐ¾Ð»ÑÑÐÑÑ ÑÐ°ÐÑÐÐºÑ ÑÐµÑÑÐÐ¹"""
    _init_engine()
    if _AsyncSessionLocal is None:
        raise ValueError("DATABASE_URL not set. Cannot initialize session factory.")
    return _AsyncSessionLocal

# ÐÐ»Ñ Ð¾ÐÑÐ°ÑÐ½Ð¾Ð¹ ÑÐ¾Ð²Ð¼ÐµÑÑÐÐ¼Ð¾ÑÑÐ - ÑÐ²Ð¾Ð¹ÑÑÐ²Ð°
class _EngineProxy:
    def __getattr__(self, name):
        return getattr(get_engine(), name)

class _SessionFactoryProxy:
    def __call__(self, *args, **kwargs):
        return get_session_factory()(*args, **kwargs)
    def __getattr__(self, name):
        return getattr(get_session_factory(), name)

engine = _EngineProxy()
AsyncSessionLocal = _SessionFactoryProxy()


async def apply_security_policies():
    """ÐÑÐÐ¼ÐµÐ½ÐÑÑ Ð¿ÑÐ°Ð²ÐÐ»Ð° ÐÐµÐ·Ð¾Ð¿Ð°ÑÐ½Ð¾ÑÑÐ ÐÐ· SQL ÑÐ°Ð¹Ð»Ð° (ÑÐ¾Ð»ÑÐºÐ¾ Ð´Ð»Ñ PostgreSQL)"""
    if not settings.DATABASE_URL.startswith("postgresql"):
        logger.info("ÐÑÐ°Ð²ÐÐ»Ð° ÐÐµÐ·Ð¾Ð¿Ð°ÑÐ½Ð¾ÑÑÐ Ð¿ÑÐÐ¼ÐµÐ½ÑÑÑÑÑ ÑÐ¾Ð»ÑÐºÐ¾ Ð´Ð»Ñ PostgreSQL. ÐÑÐ¾Ð¿ÑÑÐºÐ°ÐµÐ¼.")
        return
    
    sql_file_path = os.path.join(os.path.dirname(__file__), "security_policies.sql")
    
    if not os.path.exists(sql_file_path):
        logger.warning(f"Ð¤Ð°Ð¹Ð» Ð¿ÑÐ°Ð²ÐÐ» ÐÐµÐ·Ð¾Ð¿Ð°ÑÐ½Ð¾ÑÑÐ Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½: {sql_file_path}")
        return
    
    try:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
        
        # Ð£ÐÐÑÐ°ÐµÐ¼ Ð¼Ð½Ð¾ÐÐ¾ÑÑÑÐ¾ÑÐ½ÑÐµ ÐºÐ¾Ð¼Ð¼ÐµÐ½ÑÐ°ÑÐÐ /* ... */
        import re
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
        
        # ÐÐ°Ð·Ð´ÐµÐ»ÑÐµÐ¼ Ð½Ð° ÐºÐ¾Ð¼Ð°Ð½Ð´Ñ Ð¿Ð¾ ÑÐ¾ÑÐºÐµ Ñ Ð·Ð°Ð¿ÑÑÐ¾Ð¹
        # Ð£ÑÐÑÑÐ²Ð°ÐµÐ¼, ÑÑÐ¾ ÑÐ¾ÑÐºÐ° Ñ Ð·Ð°Ð¿ÑÑÐ¾Ð¹ Ð¼Ð¾Ð¶ÐµÑ ÐÑÑÑ Ð²Ð½ÑÑÑÐ ÑÑÑÐ¾Ðº, ÑÑÐ½ÐºÑÐÐ¹ ÐÐ»Ð dollar-quoted ÐÐ»Ð¾ÐºÐ¾Ð²
        commands = []
        current_command = []
        in_string = False
        string_char = None
        in_dollar_quote = False
        dollar_tag = None
        
        i = 0
        content_length = len(sql_content)
        
        while i < content_length:
            char = sql_content[i]
            next_chars = sql_content[i:i+10] if i + 10 < content_length else sql_content[i:]
            
            # ÐÑÐ¾Ð²ÐµÑÑÐµÐ¼ Ð½Ð°ÑÐ°Ð»Ð¾ dollar-quoted ÑÑÑÐ¾ÐºÐ ($$ ÐÐ»Ð $tag$)
            if char == '$' and not in_string and not in_dollar_quote:
                # ÐÑÐµÐ¼ Ð·Ð°ÐºÑÑÐ²Ð°ÑÑÐÐ¹ $ Ð´Ð»Ñ Ð¾Ð¿ÑÐµÐ´ÐµÐ»ÐµÐ½ÐÑ ÑÐµÐÐ°
                tag_start = i
                tag_end = i + 1
                # ÐÑÐµÐ¼ Ð¿ÐµÑÐ²ÑÐ¹ $ Ð¿Ð¾ÑÐ»Ðµ Ð¾ÑÐºÑÑÐ²Ð°ÑÑÐµÐÐ¾
                while tag_end < content_length and sql_content[tag_end] != '$':
                    tag_end += 1
                
                if tag_end < content_length:
                    tag = sql_content[tag_start:tag_end+1]
                    if not dollar_tag:
                        # ÐÐ°ÑÐ°Ð»Ð¾ dollar-quoted ÐÐ»Ð¾ÐºÐ°
                        dollar_tag = tag
                        in_dollar_quote = True
                        # ÐÐ¾ÐÐ°Ð²Ð»ÑÐµÐ¼ Ð²ÐµÑÑ ÑÐµÐ ÑÑÐ°Ð·Ñ
                        for j in range(tag_start, tag_end + 1):
                            current_command.append(sql_content[j])
                        i = tag_end + 1
                        continue
                    elif tag == dollar_tag:
                        # ÐÐ¾Ð½ÐµÑ dollar-quoted ÐÐ»Ð¾ÐºÐ°
                        dollar_tag = None
                        in_dollar_quote = False
                        # ÐÐ¾ÐÐ°Ð²Ð»ÑÐµÐ¼ Ð²ÐµÑÑ ÑÐµÐ ÑÑÐ°Ð·Ñ
                        for j in range(tag_start, tag_end + 1):
                            current_command.append(sql_content[j])
                        i = tag_end + 1
                        continue
            
            # ÐÑÐ»Ð Ð¼Ñ Ð²Ð½ÑÑÑÐ dollar-quoted ÐÐ»Ð¾ÐºÐ°, ÐÑÐµÐ¼ ÐµÐÐ¾ Ð·Ð°ÐºÑÑÑÐÐµ
            if in_dollar_quote and char == '$' and dollar_tag:
                # ÐÑÐ¾Ð²ÐµÑÑÐµÐ¼, Ð½Ðµ ÑÑÐ¾ Ð»Ð Ð·Ð°ÐºÑÑÐ²Ð°ÑÑÐÐ¹ ÑÐµÐ
                tag_len = len(dollar_tag)
                if i + tag_len - 1 < content_length:
                    potential_tag = sql_content[i:i+tag_len]
                    if potential_tag == dollar_tag:
                        # ÐÐ¾Ð½ÐµÑ dollar-quoted ÐÐ»Ð¾ÐºÐ°
                        # ÐÐ¾ÐÐ°Ð²Ð»ÑÐµÐ¼ Ð²ÐµÑÑ ÑÐµÐ
                        for j in range(i, i + tag_len):
                            current_command.append(sql_content[j])
                        i += tag_len
                        dollar_tag = None
                        in_dollar_quote = False
                        continue
            
            # ÐÐÑÐ°ÐÐ°ÑÑÐ²Ð°ÐµÐ¼ Ð¾ÐÑÑÐ½ÑÐµ ÑÑÑÐ¾ÐºÐ (ÑÐ¾Ð»ÑÐºÐ¾ ÐµÑÐ»Ð Ð½Ðµ Ð² dollar-quote)
            if not in_dollar_quote:
                if char in ("'", '"') and (not in_string or char == string_char):
                    in_string = not in_string
                    string_char = char if in_string else None
                    current_command.append(char)
                elif char == ";" and not in_string:
                    # ÐÐ¾Ð½ÐµÑ ÐºÐ¾Ð¼Ð°Ð½Ð´Ñ
                    cmd = "".join(current_command).strip()
                    if cmd:
                        commands.append(cmd)
                    current_command = []
                else:
                    current_command.append(char)
            else:
                # ÐÐ½ÑÑÑÐ dollar-quoted ÐÐ»Ð¾ÐºÐ° - Ð´Ð¾ÐÐ°Ð²Ð»ÑÐµÐ¼ Ð²ÑÐµ ÑÐÐ¼Ð²Ð¾Ð»Ñ ÐºÐ°Ðº ÐµÑÑÑ
                current_command.append(char)
            
            i += 1
        
        # ÐÐ¾ÐÐ°Ð²Ð»ÑÐµÐ¼ Ð¿Ð¾ÑÐ»ÐµÐ´Ð½ÑÑ ÐºÐ¾Ð¼Ð°Ð½Ð´Ñ ÐµÑÐ»Ð ÐµÑÑÑ
        if current_command:
            cmd = "".join(current_command).strip()
            if cmd:
                commands.append(cmd)
        
        # ÐÑÐ¿Ð¾Ð»Ð½ÑÐµÐ¼ SQL ÐºÐ¾Ð¼Ð°Ð½Ð´Ñ
        db_engine = get_engine()
        async with db_engine.begin() as conn:
            applied_count = 0
            skipped_count = 0
            
            for command in commands:
                command = command.strip()
                if not command or command.upper().startswith("--"):
                    continue
                
                try:
                    await conn.execute(text(command))
                    applied_count += 1
                    logger.debug(f" ÐÑÐÐ¼ÐµÐ½ÐµÐ½Ð° ÐºÐ¾Ð¼Ð°Ð½Ð´Ð°: {command[:60]}...")
                except Exception as e:
                    error_msg = str(e).lower()
                    # ÐÐÐ½Ð¾ÑÐÑÑÐµÐ¼ Ð¾ÑÐÐÐºÐ "ÑÐ¶Ðµ ÑÑÑÐµÑÑÐ²ÑÐµÑ" Ð´Ð»Ñ Ð¿Ð¾Ð»ÐÑÐÐº Ð ÐÐ½Ð´ÐµÐºÑÐ¾Ð²
                    if any(keyword in error_msg for keyword in [
                        "already exists", "duplicate", "does not exist"
                    ]):
                        skipped_count += 1
                        logger.debug(f"  ÐÑÐ¾Ð¿ÑÑÐµÐ½Ð° ÐºÐ¾Ð¼Ð°Ð½Ð´Ð° (ÑÐ¶Ðµ ÑÑÑÐµÑÑÐ²ÑÐµÑ): {command[:60]}...")
                    else:
                        logger.warning(f"  ÐÑÐÐÐºÐ° Ð¿ÑÐ Ð²ÑÐ¿Ð¾Ð»Ð½ÐµÐ½ÐÐ ÐºÐ¾Ð¼Ð°Ð½Ð´Ñ ÐÐµÐ·Ð¾Ð¿Ð°ÑÐ½Ð¾ÑÑÐ: {e}")
                        logger.debug(f"ÐÐ¾Ð¼Ð°Ð½Ð´Ð°: {command[:200]}")
            
            logger.info(f" ÐÑÐ°Ð²ÐÐ»Ð° ÐÐµÐ·Ð¾Ð¿Ð°ÑÐ½Ð¾ÑÑÐ Ð¿ÑÐÐ¼ÐµÐ½ÐµÐ½Ñ: {applied_count} ÐºÐ¾Ð¼Ð°Ð½Ð´, Ð¿ÑÐ¾Ð¿ÑÑÐµÐ½Ð¾: {skipped_count}")
    except Exception as e:
        logger.error(f" ÐÑÐÐÐºÐ° Ð¿ÑÐ Ð¿ÑÐÐ¼ÐµÐ½ÐµÐ½ÐÐ Ð¿ÑÐ°Ð²ÐÐ» ÐÐµÐ·Ð¾Ð¿Ð°ÑÐ½Ð¾ÑÑÐ: {e}")
        # ÐÐµ Ð¿ÑÐµÑÑÐ²Ð°ÐµÐ¼ ÐÐ½ÐÑÐÐ°Ð»ÐÐ·Ð°ÑÐÑ, ÐµÑÐ»Ð Ð½Ðµ ÑÐ´Ð°Ð»Ð¾ÑÑ Ð¿ÑÐÐ¼ÐµÐ½ÐÑÑ Ð¿ÑÐ°Ð²ÐÐ»Ð°


async def init_db():
    """ÐÐ½ÐÑÐÐ°Ð»ÐÐ·Ð°ÑÐÑ ÐÐ°Ð·Ñ Ð´Ð°Ð½Ð½ÑÑ"""
    # ÐÐ¾Ð·Ð´Ð°ÐµÐ¼ Ð´ÐÑÐµÐºÑÐ¾ÑÐÑ Ð´Ð»Ñ SQLite ÐµÑÐ»Ð ÐÑÐ¿Ð¾Ð»ÑÐ·ÑÐµÑÑÑ SQLite
    if settings.DATABASE_URL.startswith("sqlite"):
        db_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", ""))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    # ÐÐ¾Ð·Ð´Ð°ÐµÐ¼ Ð²ÑÐµ ÑÐ°ÐÐ»ÐÑÑ
    db_engine = get_engine()
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # ÐÑÐÐ¼ÐµÐ½ÑÐµÐ¼ Ð¿ÑÐ°Ð²ÐÐ»Ð° ÐÐµÐ·Ð¾Ð¿Ð°ÑÐ½Ð¾ÑÑÐ (ÑÐ¾Ð»ÑÐºÐ¾ Ð´Ð»Ñ PostgreSQL)
    await apply_security_policies()


async def get_session() -> AsyncSession:
    """ÐÐ¾Ð»ÑÑÐÑÑ ÑÐµÑÑÐÑ ÐÐ°Ð·Ñ Ð´Ð°Ð½Ð½ÑÑ"""
    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            yield session
    except ValueError as e:
        # ÐÑÐ»Ð ÐÐ°Ð·Ð° Ð´Ð°Ð½Ð½ÑÑ Ð½Ðµ ÐÐ½ÐÑÐÐ°Ð»ÐÐ·ÐÑÐ¾Ð²Ð°Ð½Ð°, ÑÐ¾Ð·Ð´Ð°ÐµÐ¼ Ð·Ð°ÐÐ»ÑÑÐºÑ
        logger.error(f"Database session error: {e}")
        # Ð production Ð»ÑÑÑÐµ Ð¿Ð¾Ð´Ð½ÑÑÑ Ð¾ÑÐÐÐºÑ, Ð½Ð¾ Ð´Ð»Ñ ÑÐ°Ð·ÑÐ°ÐÐ¾ÑÐºÐ Ð¼Ð¾Ð¶Ð½Ð¾ Ð²ÐµÑÐ½ÑÑÑ None
        # Ð Ð¾ÐÑÐ°ÐÐ¾ÑÐ°ÑÑ Ð² endpoint
        raise ValueError(f"ÐÐ°Ð·Ð° Ð´Ð°Ð½Ð½ÑÑ Ð½Ðµ Ð½Ð°ÑÑÑÐ¾ÐµÐ½Ð°: {e}")

