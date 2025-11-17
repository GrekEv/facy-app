"""Работа с базой данных"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from .models import Base
from config import settings
import os
import logging

logger = logging.getLogger(__name__)

# Ленивая инициализация движка базы данных
_engine = None
_AsyncSessionLocal = None

def _init_engine():
    """Инициализировать движок базы данных"""
    global _engine, _AsyncSessionLocal
    
    if _engine is not None:
        return  # Уже инициализирован
    
    if not settings.DATABASE_URL:
        logger.warning(
            "DATABASE_URL not set. Database operations will fail. "
            "Please set DATABASE_URL environment variable. "
            "For Vercel serverless, use PostgreSQL: postgresql+asyncpg://user:password@host:port/dbname"
        )
        # Создаем заглушку чтобы не падать при импорте
        return
    
    try:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True
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

# Инициализируем при импорте модуля (но только если DATABASE_URL установлен)
_init_engine()

# Для обратной совместимости - используем функции вместо прямого доступа
def get_engine():
    """Получить движок базы данных"""
    _init_engine()
    if _engine is None:
        raise ValueError("DATABASE_URL not set. Cannot initialize database engine.")
    return _engine

def get_session_factory():
    """Получить фабрику сессий"""
    _init_engine()
    if _AsyncSessionLocal is None:
        raise ValueError("DATABASE_URL not set. Cannot initialize session factory.")
    return _AsyncSessionLocal

# Для обратной совместимости - свойства
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
    """Применить правила безопасности из SQL файла (только для PostgreSQL)"""
    if not settings.DATABASE_URL.startswith("postgresql"):
        logger.info("Правила безопасности применяются только для PostgreSQL. Пропускаем.")
        return
    
    sql_file_path = os.path.join(os.path.dirname(__file__), "security_policies.sql")
    
    if not os.path.exists(sql_file_path):
        logger.warning(f"Файл правил безопасности не найден: {sql_file_path}")
        return
    
    try:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
        
        # Убираем многострочные комментарии /* ... */
        import re
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
        
        # Разделяем на команды по точке с запятой
        # Учитываем, что точка с запятой может быть внутри строк, функций или dollar-quoted блоков
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
            
            # Проверяем начало dollar-quoted строки ($$ или $tag$)
            if char == '$' and not in_string and not in_dollar_quote:
                # Ищем закрывающий $ для определения тега
                tag_start = i
                tag_end = i + 1
                # Ищем первый $ после открывающего
                while tag_end < content_length and sql_content[tag_end] != '$':
                    tag_end += 1
                
                if tag_end < content_length:
                    tag = sql_content[tag_start:tag_end+1]
                    if not dollar_tag:
                        # Начало dollar-quoted блока
                        dollar_tag = tag
                        in_dollar_quote = True
                        # Добавляем весь тег сразу
                        for j in range(tag_start, tag_end + 1):
                            current_command.append(sql_content[j])
                        i = tag_end + 1
                        continue
                    elif tag == dollar_tag:
                        # Конец dollar-quoted блока
                        dollar_tag = None
                        in_dollar_quote = False
                        # Добавляем весь тег сразу
                        for j in range(tag_start, tag_end + 1):
                            current_command.append(sql_content[j])
                        i = tag_end + 1
                        continue
            
            # Если мы внутри dollar-quoted блока, ищем его закрытие
            if in_dollar_quote and char == '$' and dollar_tag:
                # Проверяем, не это ли закрывающий тег
                tag_len = len(dollar_tag)
                if i + tag_len - 1 < content_length:
                    potential_tag = sql_content[i:i+tag_len]
                    if potential_tag == dollar_tag:
                        # Конец dollar-quoted блока
                        # Добавляем весь тег
                        for j in range(i, i + tag_len):
                            current_command.append(sql_content[j])
                        i += tag_len
                        dollar_tag = None
                        in_dollar_quote = False
                        continue
            
            # Обрабатываем обычные строки (только если не в dollar-quote)
            if not in_dollar_quote:
                if char in ("'", '"') and (not in_string or char == string_char):
                    in_string = not in_string
                    string_char = char if in_string else None
                    current_command.append(char)
                elif char == ";" and not in_string:
                    # Конец команды
                    cmd = "".join(current_command).strip()
                    if cmd:
                        commands.append(cmd)
                    current_command = []
                else:
                    current_command.append(char)
            else:
                # Внутри dollar-quoted блока - добавляем все символы как есть
                current_command.append(char)
            
            i += 1
        
        # Добавляем последнюю команду если есть
        if current_command:
            cmd = "".join(current_command).strip()
            if cmd:
                commands.append(cmd)
        
        # Выполняем SQL команды
        async with engine.begin() as conn:
            applied_count = 0
            skipped_count = 0
            
            for command in commands:
                command = command.strip()
                if not command or command.upper().startswith("--"):
                    continue
                
                try:
                    await conn.execute(text(command))
                    applied_count += 1
                    logger.debug(f"✅ Применена команда: {command[:60]}...")
                except Exception as e:
                    error_msg = str(e).lower()
                    # Игнорируем ошибки "уже существует" для политик и индексов
                    if any(keyword in error_msg for keyword in [
                        "already exists", "duplicate", "does not exist"
                    ]):
                        skipped_count += 1
                        logger.debug(f"⏭️  Пропущена команда (уже существует): {command[:60]}...")
                    else:
                        logger.warning(f"⚠️  Ошибка при выполнении команды безопасности: {e}")
                        logger.debug(f"Команда: {command[:200]}")
            
            logger.info(f"✅ Правила безопасности применены: {applied_count} команд, пропущено: {skipped_count}")
    except Exception as e:
        logger.error(f"❌ Ошибка при применении правил безопасности: {e}")
        # Не прерываем инициализацию, если не удалось применить правила


async def init_db():
    """Инициализация базы данных"""
    # Создаем директорию для SQLite если используется SQLite
    if settings.DATABASE_URL.startswith("sqlite"):
        db_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", ""))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    # Создаем все таблицы
    db_engine = get_engine()
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Применяем правила безопасности (только для PostgreSQL)
    await apply_security_policies()


async def get_session() -> AsyncSession:
    """Получить сессию базы данных"""
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session

