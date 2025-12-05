# Supabase 详细设置指南

## 📋 第一步：创建 Supabase 项目

1. 访问 https://supabase.com
2. 点击右上角 **Sign In** 登录（如果没有账号，先注册）
3. 登录后，点击 **New Project**
4. 填写项目信息：
   - **Name**: `moodjournal`（或你喜欢的名字）
   - **Database Password**: 设置一个强密码（**请务必保存好！**）
   - **Region**: 选择离你最近的区域
     - 中国大陆用户推荐：`Southeast Asia (Singapore)` 或 `Northeast Asia (Tokyo)`
     - 其他地区选择最近的即可
5. 点击 **Create new project**
6. 等待项目创建完成（约 2-3 分钟）

---

## 🗄️ 第二步：创建数据库表

### 2.1 打开 SQL Editor

1. 在 Supabase Dashboard 左侧菜单，点击 **SQL Editor**
2. 点击右上角的 **New Query** 按钮

### 2.2 执行 SQL 脚本

1. 打开项目中的 `supabase_setup.sql` 文件
2. **复制全部内容**（Ctrl+A 全选，Ctrl+C 复制）
3. 粘贴到 Supabase SQL Editor 中
4. 点击右下角的 **Run** 按钮（或按 `Ctrl+Enter`）
5. 等待执行完成，应该看到类似 "Success. No rows returned" 的消息

### 2.3 验证表是否创建成功

1. 在左侧菜单，点击 **Table Editor**
2. 你应该能看到 `journals` 表
3. 点击 `journals` 表，查看表结构：
   - `id` (uuid)
   - `date` (text)
   - `weather` (text)
   - `text` (text)
   - `image_paths` (text[])
   - `journal_image_url` (text)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

✅ **注意**：SQL 脚本**只创建数据表**，Storage bucket 需要单独在 UI 中创建（见下一步）

---

## 📦 第三步：创建 Storage Bucket（重要！）

Storage bucket 用于存储图片，**必须手动创建**，不能通过 SQL 创建。

### 3.1 进入 Storage 页面

1. 在 Supabase Dashboard 左侧菜单，点击 **Storage**
2. 如果看到 "No buckets yet"，说明还没有创建任何 bucket

### 3.2 创建新 Bucket

1. 点击右上角的 **New bucket** 按钮（或 **Create a new bucket**）
2. 填写信息：
   - **Name**: `journal-images`（**必须完全一致**，包括大小写）
   - **Public bucket**: ✅ **必须勾选**（这样图片才能公开访问，应用才能显示）
3. 点击 **Create bucket**

### 3.3 设置 Bucket 权限（重要！）

创建 bucket 后，需要设置访问权限：

#### 方法 1：使用 Policy Templates（推荐，简单）

1. 在 Storage 页面，点击刚创建的 `journal-images` bucket
2. 点击 **Policies** 标签
3. 点击 **New Policy**
4. 选择 **For full customization**
5. 在 Policy 名称输入：`Public Access`
6. 在 Policy definition 中输入：

```sql
-- 允许所有人读取
(bucket_id = 'journal-images')
```

7. 在 Allowed operation 中选择：**SELECT**（读取）
8. 点击 **Review** → **Save policy**

#### 方法 2：使用 SQL（更灵活）

1. 在 **SQL Editor** 中，执行以下 SQL：

```sql
-- 允许所有人读取图片
CREATE POLICY "Public Access for journal-images"
ON storage.objects
FOR SELECT
USING (bucket_id = 'journal-images');

-- 允许所有人上传图片（如果需要，可以改为只允许认证用户）
CREATE POLICY "Public Upload for journal-images"
ON storage.objects
FOR INSERT
WITH CHECK (bucket_id = 'journal-images');
```

### 3.4 验证 Bucket 创建成功

1. 在 Storage 页面，应该能看到 `journal-images` bucket
2. 点击进入 bucket，应该能看到 **Policies** 标签下有权限策略
3. 确认 bucket 是 **Public** 状态（应该显示一个地球图标 🌍）

---

## 🔑 第四步：获取 API 凭证

### 4.1 进入 API 设置页面

1. 在 Supabase Dashboard 左侧菜单，点击 **Settings**（齿轮图标）
2. 点击 **API**

### 4.2 复制凭证

在 **Project API keys** 部分，找到：

1. **Project URL**：
   - 格式类似：`https://xxxxxxxxxxxxx.supabase.co`
   - 点击右侧的复制图标 📋
   - **这就是 `SUPABASE_URL`**

2. **anon public** key：
   - 格式类似：`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`（很长的一串）
   - 点击右侧的复制图标 📋
   - **这就是 `SUPABASE_KEY`**

⚠️ **重要提示**：
- 使用 `anon public` key（不是 `service_role` key）
- `service_role` key 权限太高，不要在前端使用
- 保存好这两个值，后续部署时需要用到

---

## ✅ 验证设置

### 测试数据库连接

1. 在 **Table Editor** → `journals` 表中
2. 点击 **Insert row**
3. 填写测试数据：
   - `date`: `2025年12月05日`
   - `weather`: `☀️ 晴天`
   - `text`: `测试`
4. 点击 **Save**
5. 如果成功保存，说明数据库设置正确 ✅

### 测试 Storage

1. 在 **Storage** → `journal-images` bucket 中
2. 点击 **Upload file**
3. 上传一张测试图片
4. 上传成功后，点击图片
5. 应该能看到图片的 **Public URL**
6. 复制这个 URL，在浏览器中打开，应该能看到图片 ✅

---

## 🎉 完成！

现在你已经完成了 Supabase 的设置：
- ✅ 数据库表 `journals` 已创建
- ✅ Storage bucket `journal-images` 已创建并设置为 Public
- ✅ 已获取 `SUPABASE_URL` 和 `SUPABASE_KEY`

**下一步**：将这些凭证添加到 Vercel 环境变量中，或保存到本地 `.env` 文件中。

---

## ❓ 常见问题

### Q: 为什么 SQL 脚本没有创建 Storage bucket？
A: Storage bucket 必须在 Supabase Dashboard 的 UI 中手动创建，不能通过 SQL 创建。这是 Supabase 的设计。

### Q: Bucket 必须是 Public 吗？
A: 是的，因为应用需要直接通过 URL 访问图片。如果设置为 Private，需要额外的认证步骤，会更复杂。

### Q: 如何修改 Bucket 名称？
A: 如果已经创建了其他名称的 bucket，可以：
1. 删除现有 bucket（注意：会删除所有文件）
2. 重新创建名为 `journal-images` 的 bucket
3. 或者修改 `supabase_config.py` 中的 `SUPABASE_BUCKET` 变量

### Q: 忘记保存凭证怎么办？
A: 随时可以在 **Settings → API** 中重新查看和复制。

