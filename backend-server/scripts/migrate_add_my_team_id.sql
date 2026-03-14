-- 数据库迁移脚本：添加 my_team_id 字段到 users 表
-- 日期：2026-03-14
-- 说明：简化用户球队关系，每个用户只有一个球队

-- 添加 my_team_id 列
ALTER TABLE users ADD COLUMN my_team_id INTEGER REFERENCES teams(id) ON DELETE SET NULL;

-- 为现有用户设置 my_team_id（根据他们的 team_members 记录）
-- 如果用户有多个球队，选择权限最高的
UPDATE users
SET my_team_id = (
    SELECT DISTINCT ON (user_id) team_id
    FROM team_members
    WHERE team_members.user_id = users.id
    AND team_members.is_active = true
    ORDER BY
        CASE permission
            WHEN 'owner' THEN 1
            WHEN 'admin' THEN 2
            WHEN 'member' THEN 3
        END,
        created_at ASC
);

-- 创建索引以提高查询性能
CREATE INDEX idx_users_my_team_id ON users(my_team_id);

-- 验证迁移结果
-- SELECT id, username, my_team_id FROM users;
