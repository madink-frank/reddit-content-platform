-- Reddit Content Platform - Initial Schema Migration for Supabase
-- This creates all the necessary tables, indexes, and security policies

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reddit_username VARCHAR(255) UNIQUE NOT NULL,
    reddit_id VARCHAR(255) UNIQUE NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Keywords table for tracking topics
CREATE TABLE IF NOT EXISTS keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    keyword VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, keyword)
);

-- Posts table for storing Reddit posts
CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reddit_id VARCHAR(255) UNIQUE NOT NULL,
    keyword_id UUID NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT,
    author VARCHAR(255),
    subreddit VARCHAR(255),
    url TEXT,
    score INTEGER DEFAULT 0,
    num_comments INTEGER DEFAULT 0,
    created_utc TIMESTAMP WITH TIME ZONE,
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Comments table for storing Reddit comments
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reddit_id VARCHAR(255) UNIQUE NOT NULL,
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    author VARCHAR(255),
    content TEXT,
    score INTEGER DEFAULT 0,
    created_utc TIMESTAMP WITH TIME ZONE,
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Metrics table for storing analysis results
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword_id UUID NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    metric_type VARCHAR(100) NOT NULL,
    metric_value JSONB NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Blog content table for generated content
CREATE TABLE IF NOT EXISTS blog_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword_id UUID NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    tags TEXT[],
    status VARCHAR(50) DEFAULT 'draft',
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Process logs table for tracking background tasks
CREATE TABLE IF NOT EXISTS process_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    process_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    details JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_reddit_username ON users(reddit_username);
CREATE INDEX IF NOT EXISTS idx_users_reddit_id ON users(reddit_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_keywords_user_id ON keywords(user_id);
CREATE INDEX IF NOT EXISTS idx_keywords_active ON keywords(is_active);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);

CREATE INDEX IF NOT EXISTS idx_posts_reddit_id ON posts(reddit_id);
CREATE INDEX IF NOT EXISTS idx_posts_keyword_id ON posts(keyword_id);
CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts(subreddit);
CREATE INDEX IF NOT EXISTS idx_posts_created_utc ON posts(created_utc);
CREATE INDEX IF NOT EXISTS idx_posts_score ON posts(score);
CREATE INDEX IF NOT EXISTS idx_posts_keyword_created ON posts(keyword_id, created_utc DESC);

CREATE INDEX IF NOT EXISTS idx_comments_reddit_id ON comments(reddit_id);
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON comments(parent_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_utc ON comments(created_utc);

CREATE INDEX IF NOT EXISTS idx_metrics_keyword_id ON metrics(keyword_id);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_metrics_calculated_at ON metrics(calculated_at);

CREATE INDEX IF NOT EXISTS idx_blog_content_keyword_id ON blog_content(keyword_id);
CREATE INDEX IF NOT EXISTS idx_blog_content_status ON blog_content(status);
CREATE INDEX IF NOT EXISTS idx_blog_content_published_at ON blog_content(published_at);

CREATE INDEX IF NOT EXISTS idx_process_logs_type ON process_logs(process_type);
CREATE INDEX IF NOT EXISTS idx_process_logs_status ON process_logs(status);
CREATE INDEX IF NOT EXISTS idx_process_logs_started_at ON process_logs(started_at);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_posts_title_fts ON posts USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_posts_content_fts ON posts USING gin(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_comments_content_fts ON comments USING gin(to_tsvector('english', content));

-- Trigram indexes for fuzzy search
CREATE INDEX IF NOT EXISTS idx_posts_title_trgm ON posts USING gin(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword_trgm ON keywords USING gin(keyword gin_trgm_ops);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_keywords_updated_at BEFORE UPDATE ON keywords FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_metrics_updated_at BEFORE UPDATE ON metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_blog_content_updated_at BEFORE UPDATE ON blog_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_process_logs_updated_at BEFORE UPDATE ON process_logs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE process_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid()::text = id::text);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid()::text = id::text);

-- Keywords policies
CREATE POLICY "Users can view own keywords" ON keywords FOR SELECT USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can insert own keywords" ON keywords FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
CREATE POLICY "Users can update own keywords" ON keywords FOR UPDATE USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can delete own keywords" ON keywords FOR DELETE USING (auth.uid()::text = user_id::text);

-- Posts policies (users can see posts from their keywords)
CREATE POLICY "Users can view posts from own keywords" ON posts FOR SELECT USING (
    keyword_id IN (SELECT id FROM keywords WHERE user_id::text = auth.uid()::text)
);

-- Comments policies (users can see comments from posts of their keywords)
CREATE POLICY "Users can view comments from own posts" ON comments FOR SELECT USING (
    post_id IN (
        SELECT p.id FROM posts p 
        JOIN keywords k ON p.keyword_id = k.id 
        WHERE k.user_id::text = auth.uid()::text
    )
);

-- Metrics policies
CREATE POLICY "Users can view own metrics" ON metrics FOR SELECT USING (
    keyword_id IN (SELECT id FROM keywords WHERE user_id::text = auth.uid()::text)
);

-- Blog content policies
CREATE POLICY "Users can view own blog content" ON blog_content FOR SELECT USING (
    keyword_id IN (SELECT id FROM keywords WHERE user_id::text = auth.uid()::text)
);
CREATE POLICY "Users can insert own blog content" ON blog_content FOR INSERT WITH CHECK (
    keyword_id IN (SELECT id FROM keywords WHERE user_id::text = auth.uid()::text)
);
CREATE POLICY "Users can update own blog content" ON blog_content FOR UPDATE USING (
    keyword_id IN (SELECT id FROM keywords WHERE user_id::text = auth.uid()::text)
);
CREATE POLICY "Users can delete own blog content" ON blog_content FOR DELETE USING (
    keyword_id IN (SELECT id FROM keywords WHERE user_id::text = auth.uid()::text)
);

-- Process logs policies (users can view their own process logs)
CREATE POLICY "Users can view own process logs" ON process_logs FOR SELECT USING (
    details->>'user_id' = auth.uid()::text
);

-- Public policies for blog content (for public blog site)
CREATE POLICY "Public can view published blog content" ON blog_content FOR SELECT USING (
    status = 'published'
);

-- Insert some sample data for testing (optional)
-- This will be executed only if tables are empty
DO $$
BEGIN
    -- Only insert if users table is empty
    IF NOT EXISTS (SELECT 1 FROM users LIMIT 1) THEN
        -- Insert a demo user
        INSERT INTO users (id, reddit_username, reddit_id, is_active) 
        VALUES (
            '00000000-0000-0000-0000-000000000001',
            'demo_user',
            'demo_reddit_id',
            true
        );
        
        -- Insert demo keywords
        INSERT INTO keywords (id, user_id, keyword, is_active) VALUES
        ('00000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'python', true),
        ('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', 'javascript', true),
        ('00000000-0000-0000-0000-000000000004', '00000000-0000-0000-0000-000000000001', 'react', true);
    END IF;
END $$;