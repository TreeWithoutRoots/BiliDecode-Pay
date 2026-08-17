-- BiliDecode 分析历史表
-- 在 Supabase Dashboard > SQL Editor 中执行此脚本

CREATE TABLE IF NOT EXISTS analysis_history (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    bvid            TEXT NOT NULL,
    title           TEXT,
    video_url       TEXT,
    up_name         TEXT,
    cover_url       TEXT,
    view_count      BIGINT DEFAULT 0,
    like_count      BIGINT DEFAULT 0,
    coin_count      BIGINT DEFAULT 0,
    favorite_count  BIGINT DEFAULT 0,
    report_text     TEXT,
    model_used      TEXT,
    input_tokens    INT DEFAULT 0,
    output_tokens   INT DEFAULT 0,
    estimated_cost  FLOAT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 按时间倒序索引
CREATE INDEX IF NOT EXISTS idx_analysis_created_at
    ON analysis_history (created_at DESC);

-- 按 BVID 索引（查重）
CREATE INDEX IF NOT EXISTS idx_analysis_bvid
    ON analysis_history (bvid);

-- 启用 Row Level Security
ALTER TABLE analysis_history ENABLE ROW LEVEL SECURITY;

-- 允许所有人读写（本项目为个人工具，无多租户需求）
CREATE POLICY "allow_all_select" ON analysis_history
    FOR SELECT USING (true);
CREATE POLICY "allow_all_insert" ON analysis_history
    FOR INSERT WITH CHECK (true);
CREATE POLICY "allow_all_update" ON analysis_history
    FOR UPDATE USING (true);
CREATE POLICY "allow_all_delete" ON analysis_history
    FOR DELETE USING (true);
