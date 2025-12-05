-- ==========================================
-- MoodJournal Supabase 数据库表结构
-- ==========================================

-- 1. 创建 journals 表（存储日记条目）
CREATE TABLE IF NOT EXISTS journals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date TEXT NOT NULL,
    weather TEXT NOT NULL,
    text TEXT NOT NULL,
    image_paths TEXT[] DEFAULT '{}',  -- 存储图片URL数组
    journal_image_url TEXT,  -- 生成的手账图片URL
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 创建索引以优化查询
CREATE INDEX IF NOT EXISTS idx_journals_date ON journals(date);
CREATE INDEX IF NOT EXISTS idx_journals_created_at ON journals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_journals_weather ON journals(weather);

-- 3. 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_journals_updated_at 
    BEFORE UPDATE ON journals 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 4. 启用 Row Level Security (RLS) - 可选，如果只需要个人使用可以关闭
-- ALTER TABLE journals ENABLE ROW LEVEL SECURITY;

-- 5. 如果需要公开访问（个人使用），可以创建策略
-- CREATE POLICY "Allow all operations for authenticated users" ON journals
--     FOR ALL USING (true);

-- 注意：如果这是个人项目，可以暂时禁用RLS
-- ALTER TABLE journals DISABLE ROW LEVEL SECURITY;

