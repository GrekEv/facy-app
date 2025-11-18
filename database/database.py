"""�а�ота � �азой данн��"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from .models import Base
from config import settings
import os
import logging

logger = logging.getLogger(__name__)

# Лен�ва� �н�ц�ал�зац�� дв�жка �аз� данн��
_engine = None
_AsyncSessionLocal = None

def _init_engine():
    """Ин�ц�ал�з��оват� дв�жок �аз� данн��"""
    global _engine, _AsyncSessionLocal
    
    if _engine is not None:
        return  # Уже �н�ц�ал�з��ован
    
    if not settings.DATABASE_URL:
        logger.warning(
            "DATABASE_URL not set. Database operations will fail. "
            "Please set DATABASE_URL environment variable. "
            "For Vercel serverless, use PostgreSQL: postgresql+asyncpg://user:password@host:port/dbname"
        )
        # �оздаем за�лушку что�� не падат� п�� �мпо�те
        return
    
    # �втомат�че�кое п�ео��азован�е �танда�тно�о PostgreSQL URL дл� asyncpg
    database_url = settings.DATABASE_URL
    ssl_required = False
    
    # ��ове��ем нал�ч�е sslmode=require в URL
    if "sslmode=require" in database_url:
        ssl_required = True
        # У���аем па�амет� sslmode �з URL (asyncpg не подде�ж�вает е�о в URL)
        database_url = database_url.replace("?sslmode=require", "").replace("&sslmode=require", "")
    
    if database_url.startswith("postgresql://") and not database_url.startswith("postgresql+asyncpg://"):
        # ��ео��азуем �танда�тн�й PostgreSQL URL дл� asyncpg
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        logger.info("Converted PostgreSQL URL to asyncpg format for Neon/Postgres compatibility")
    
    # �а�т�ойка SSL дл� Neon � д�у��� п�овайде�ов, т�е�у���� SSL
    connect_args = {}
    if ssl_required:
        import ssl
        connect_args["ssl"] = ssl.create_default_context()
        logger.info("SSL enabled for database connection (Neon/Postgres)")
    
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

# Ин�ц�ал�з��уем п�� �мпо�те модул� (но тол�ко е�л� DATABASE_URL у�тановлен)
_init_engine()

# �л� о��атной �овме�т�мо�т� - ��пол�зуем функц�� вме�то п��мо�о до�тупа
def get_engine():
    """�олуч�т� дв�жок �аз� данн��"""
    _init_engine()
    if _engine is None:
        raise ValueError("DATABASE_URL not set. Cannot initialize database engine.")
    return _engine

def get_session_factory():
    """�олуч�т� фа���ку �е���й"""
    _init_engine()
    if _AsyncSessionLocal is None:
        raise ValueError("DATABASE_URL not set. Cannot initialize session factory.")
    return _AsyncSessionLocal

# �л� о��атной �овме�т�мо�т� - �вой�тва
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
    """���мен�т� п�ав�ла �езопа�но�т� �з SQL файла (тол�ко дл� PostgreSQL)"""
    if not settings.DATABASE_URL.startswith("postgresql"):
        logger.info("��ав�ла �езопа�но�т� п��мен��т�� тол�ко дл� PostgreSQL. ��опу�каем.")
        return
    
    sql_file_path = os.path.join(os.path.dirname(__file__), "security_policies.sql")
    
    if not os.path.exists(sql_file_path):
        logger.warning(f"Файл п�ав�л �езопа�но�т� не найден: {sql_file_path}")
        return
    
    try:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
        
        # У���аем мно�о�т�очн�е коммента��� /* ... */
        import re
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
        
        # �аздел�ем на команд� по точке � зап�той
        # Уч�т�ваем, что точка � зап�той может ��т� внут�� �т�ок, функц�й �л� dollar-quoted �локов
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
            
            # ��ове��ем начало dollar-quoted �т�ок� ($$ �л� $tag$)
            if char == '$' and not in_string and not in_dollar_quote:
                # И�ем зак��ва���й $ дл� оп�еделен�� те�а
                tag_start = i
                tag_end = i + 1
                # И�ем пе�в�й $ по�ле отк��ва��е�о
                while tag_end < content_length and sql_content[tag_end] != '$':
                    tag_end += 1
                
                if tag_end < content_length:
                    tag = sql_content[tag_start:tag_end+1]
                    if not dollar_tag:
                        # �ачало dollar-quoted �лока
                        dollar_tag = tag
                        in_dollar_quote = True
                        # �о�авл�ем ве�� те� ��азу
                        for j in range(tag_start, tag_end + 1):
                            current_command.append(sql_content[j])
                        i = tag_end + 1
                        continue
                    elif tag == dollar_tag:
                        # �онец dollar-quoted �лока
                        dollar_tag = None
                        in_dollar_quote = False
                        # �о�авл�ем ве�� те� ��азу
                        for j in range(tag_start, tag_end + 1):
                            current_command.append(sql_content[j])
                        i = tag_end + 1
                        continue
            
            # Е�л� м� внут�� dollar-quoted �лока, ��ем е�о зак��т�е
            if in_dollar_quote and char == '$' and dollar_tag:
                # ��ове��ем, не �то л� зак��ва���й те�
                tag_len = len(dollar_tag)
                if i + tag_len - 1 < content_length:
                    potential_tag = sql_content[i:i+tag_len]
                    if potential_tag == dollar_tag:
                        # �онец dollar-quoted �лока
                        # �о�авл�ем ве�� те�
                        for j in range(i, i + tag_len):
                            current_command.append(sql_content[j])
                        i += tag_len
                        dollar_tag = None
                        in_dollar_quote = False
                        continue
            
            # О��а�ат�ваем о��чн�е �т�ок� (тол�ко е�л� не в dollar-quote)
            if not in_dollar_quote:
                if char in ("'", '"') and (not in_string or char == string_char):
                    in_string = not in_string
                    string_char = char if in_string else None
                    current_command.append(char)
                elif char == ";" and not in_string:
                    # �онец команд�
                    cmd = "".join(current_command).strip()
                    if cmd:
                        commands.append(cmd)
                    current_command = []
                else:
                    current_command.append(char)
            else:
                # �нут�� dollar-quoted �лока - до�авл�ем в�е ��мвол� как е�т�
                current_command.append(char)
            
            i += 1
        
        # �о�авл�ем по�ледн�� команду е�л� е�т�
        if current_command:
            cmd = "".join(current_command).strip()
            if cmd:
                commands.append(cmd)
        
        # ��полн�ем SQL команд�
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
                    logger.debug(f" ���менена команда: {command[:60]}...")
                except Exception as e:
                    error_msg = str(e).lower()
                    # И�но���уем ош��к� "уже �у�е�твует" дл� пол�т�к � �ндек�ов
                    if any(keyword in error_msg for keyword in [
                        "already exists", "duplicate", "does not exist"
                    ]):
                        skipped_count += 1
                        logger.debug(f"  ��опу�ена команда (уже �у�е�твует): {command[:60]}...")
                    else:
                        logger.warning(f"  Ош��ка п�� в�полнен�� команд� �езопа�но�т�: {e}")
                        logger.debug(f"�оманда: {command[:200]}")
            
            logger.info(f" ��ав�ла �езопа�но�т� п��менен�: {applied_count} команд, п�опу�ено: {skipped_count}")
    except Exception as e:
        logger.error(f" Ош��ка п�� п��менен�� п�ав�л �езопа�но�т�: {e}")
        # �е п�е��ваем �н�ц�ал�зац��, е�л� не удало�� п��мен�т� п�ав�ла


async def init_db():
    """Ин�ц�ал�зац�� �аз� данн��"""
    # �оздаем д��екто��� дл� SQLite е�л� ��пол�зует�� SQLite
    if settings.DATABASE_URL.startswith("sqlite"):
        db_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", ""))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    # �оздаем в�е та�л�ц�
    db_engine = get_engine()
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # ���мен�ем п�ав�ла �езопа�но�т� (тол�ко дл� PostgreSQL)
    await apply_security_policies()


async def get_session() -> AsyncSession:
    """�олуч�т� �е���� �аз� данн��"""
    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            yield session
    except ValueError as e:
        # Е�л� �аза данн�� не �н�ц�ал�з��ована, �оздаем за�лушку
        logger.error(f"Database session error: {e}")
        # � production лучше подн�т� ош��ку, но дл� �аз�а�отк� можно ве�нут� None
        # � о��а�отат� в endpoint
        raise ValueError(f"База данн�� не на�т�оена: {e}")

