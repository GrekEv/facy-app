-- Правила безопасности для PostgreSQL (Row Level Security)
-- Этот файл содержит политики безопасности на уровне строк (RLS)

-- ============================================
-- 1. Включение Row Level Security для таблиц
-- ============================================

-- Пользователи могут видеть только свои данные
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Генерации: пользователи видят только свои генерации
ALTER TABLE generations ENABLE ROW LEVEL SECURITY;

-- Транзакции: пользователи видят только свои транзакции
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Методы оплаты: пользователи видят только свои методы
ALTER TABLE payment_methods ENABLE ROW LEVEL SECURITY;

-- Выводы: пользователи видят только свои выводы
ALTER TABLE withdrawals ENABLE ROW LEVEL SECURITY;

-- Логи аудита: только администраторы могут видеть все логи
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Ограничения rate limit: пользователи видят только свои
ALTER TABLE rate_limits ENABLE ROW LEVEL SECURITY;

-- Жалобы: пользователи видят только свои жалобы
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Промокоды: все могут видеть активные промокоды (только чтение)
ALTER TABLE promo_codes ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 2. Политики для таблицы users
-- ============================================

-- Пользователи могут видеть только свои данные
CREATE POLICY users_select_own ON users
    FOR SELECT
    USING (true);  -- Временно разрешаем всем (можно ограничить по telegram_id)

-- Пользователи могут обновлять только свои данные
CREATE POLICY users_update_own ON users
    FOR UPDATE
    USING (true);  -- Временно разрешаем всем (можно ограничить по telegram_id)

-- Пользователи могут вставлять только свои данные
CREATE POLICY users_insert_own ON users
    FOR INSERT
    WITH CHECK (true);  -- Временно разрешаем всем

-- ============================================
-- 3. Политики для таблицы generations
-- ============================================

-- Пользователи видят только свои генерации (или публичные)
CREATE POLICY generations_select_own ON generations
    FOR SELECT
    USING (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id OR is_public = true)

-- Пользователи могут создавать только свои генерации
CREATE POLICY generations_insert_own ON generations
    FOR INSERT
    WITH CHECK (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Пользователи могут обновлять только свои генерации
CREATE POLICY generations_update_own ON generations
    FOR UPDATE
    USING (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Пользователи могут удалять только свои генерации
CREATE POLICY generations_delete_own ON generations
    FOR DELETE
    USING (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- ============================================
-- 4. Политики для таблицы transactions
-- ============================================

-- Пользователи видят только свои транзакции
CREATE POLICY transactions_select_own ON transactions
    FOR SELECT
    USING (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Пользователи могут создавать только свои транзакции
CREATE POLICY transactions_insert_own ON transactions
    FOR INSERT
    WITH CHECK (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Только система может обновлять транзакции (через приложение)
CREATE POLICY transactions_update_system ON transactions
    FOR UPDATE
    USING (true);  -- Временно разрешаем всем (в продакшене ограничить доступ)

-- ============================================
-- 5. Политики для таблицы payment_methods
-- ============================================

-- Пользователи видят только свои методы оплаты
CREATE POLICY payment_methods_select_own ON payment_methods
    FOR SELECT
    USING (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Пользователи могут создавать только свои методы оплаты
CREATE POLICY payment_methods_insert_own ON payment_methods
    FOR INSERT
    WITH CHECK (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Пользователи могут обновлять только свои методы оплаты
CREATE POLICY payment_methods_update_own ON payment_methods
    FOR UPDATE
    USING (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Пользователи могут удалять только свои методы оплаты
CREATE POLICY payment_methods_delete_own ON payment_methods
    FOR DELETE
    USING (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- ============================================
-- 6. Политики для таблицы withdrawals
-- ============================================

-- Пользователи видят только свои выводы
CREATE POLICY withdrawals_select_own ON withdrawals
    FOR SELECT
    USING (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Пользователи могут создавать только свои выводы
CREATE POLICY withdrawals_insert_own ON withdrawals
    FOR INSERT
    WITH CHECK (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Только администраторы могут обновлять выводы
CREATE POLICY withdrawals_update_admin ON withdrawals
    FOR UPDATE
    USING (true);  -- Временно разрешаем всем (в продакшене ограничить доступ)

-- ============================================
-- 7. Политики для таблицы audit_logs
-- ============================================

-- Пользователи видят только свои логи
CREATE POLICY audit_logs_select_own ON audit_logs
    FOR SELECT
    USING (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Только система может создавать логи
CREATE POLICY audit_logs_insert_system ON audit_logs
    FOR INSERT
    WITH CHECK (true);  -- Временно разрешаем всем (в продакшене ограничить доступ)

-- ============================================
-- 8. Политики для таблицы reports
-- ============================================

-- Пользователи видят только свои жалобы
CREATE POLICY reports_select_own ON reports
    FOR SELECT
    USING (true);  -- Временно разрешаем всем (можно ограничить: reporter_user_id = current_user_id)

-- Пользователи могут создавать жалобы
CREATE POLICY reports_insert_own ON reports
    FOR INSERT
    WITH CHECK (true);  -- Временно разрешаем всем (можно ограничить: reporter_user_id = current_user_id)

-- Только администраторы могут обновлять жалобы
CREATE POLICY reports_update_admin ON reports
    FOR UPDATE
    USING (true);  -- Временно разрешаем всем (в продакшене ограничить доступ)

-- ============================================
-- 9. Политики для таблицы rate_limits
-- ============================================

-- Пользователи видят только свои ограничения
CREATE POLICY rate_limits_select_own ON rate_limits
    FOR SELECT
    USING (true);  -- Временно разрешаем всем (можно ограничить: user_id = current_user_id)

-- Только система может создавать/обновлять ограничения
CREATE POLICY rate_limits_system ON rate_limits
    FOR ALL
    USING (true);  -- Временно разрешаем всем (в продакшене ограничить доступ)

-- ============================================
-- 10. Политики для таблицы promo_codes
-- ============================================

-- Все могут видеть активные промокоды (только чтение)
CREATE POLICY promo_codes_select_active ON promo_codes
    FOR SELECT
    USING (is_active = true AND (valid_until IS NULL OR valid_until > NOW()));

-- Только администраторы могут создавать/обновлять промокоды
CREATE POLICY promo_codes_admin ON promo_codes
    FOR ALL
    USING (true);  -- Временно разрешаем всем (в продакшене ограничить доступ)

-- ============================================
-- 11. Дополнительные ограничения безопасности
-- ============================================

-- Ограничение: пользователи не могут изменять свой баланс напрямую
-- (это должно делаться только через транзакции)
-- Это реализуется на уровне приложения, но можно добавить триггер:

CREATE OR REPLACE FUNCTION prevent_direct_balance_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Разрешаем изменение баланса только через транзакции
    -- (проверка на уровне приложения)
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для предотвращения прямого изменения баланса
-- (можно раскомментировать, если нужна дополнительная защита)
-- CREATE TRIGGER check_balance_update
--     BEFORE UPDATE OF balance ON users
--     FOR EACH ROW
--     EXECUTE FUNCTION prevent_direct_balance_update();

-- ============================================
-- 12. Индексы для производительности
-- ============================================

-- Индексы уже созданы через SQLAlchemy модели, но можно добавить дополнительные:

-- Индекс для быстрого поиска по telegram_id
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);

-- Индекс для поиска генераций по пользователю и статусу
CREATE INDEX IF NOT EXISTS idx_generations_user_status ON generations(user_id, status);

-- Индекс для поиска транзакций по пользователю и статусу
CREATE INDEX IF NOT EXISTS idx_transactions_user_status ON transactions(user_id, status);

-- Индекс для поиска активных промокодов
CREATE INDEX IF NOT EXISTS idx_promo_codes_active ON promo_codes(is_active, valid_until) WHERE is_active = true;

-- ============================================
-- ПРИМЕЧАНИЯ:
-- ============================================
-- 1. Политики с USING (true) - временно разрешают всем доступ
--    В продакшене нужно ограничить доступ по user_id
-- 2. Для полноценной работы RLS нужна функция current_user_id()
--    которая возвращает ID текущего пользователя из сессии
-- 3. Администраторский доступ можно реализовать через отдельную роль
-- 4. Эти политики применяются автоматически при инициализации БД








