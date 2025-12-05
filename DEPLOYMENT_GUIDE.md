# MoodJournal 部署指南

本指南将帮助你将 MoodJournal 部署到 Supabase + Vercel。

## 📋 前置准备

1. **Supabase 账号**：访问 https://supabase.com 注册账号
2. **Vercel 账号**：访问 https://vercel.com 注册账号（可使用 GitHub 登录）
3. **GitHub 账号**：用于代码仓库

---

## 🗄️ 第一步：设置 Supabase 数据库

### 1.1 创建 Supabase 项目

1. 登录 Supabase Dashboard
2. 点击 "New Project"
3. 填写项目信息：
   - **Name**: `moodjournal`（或你喜欢的名字）
   - **Database Password**: 设置一个强密码（**请保存好！**）
   - **Region**: 选择离你最近的区域（如 `Southeast Asia (Singapore)`）
4. 等待项目创建完成（约 2 分钟）

### 1.2 创建数据库表

1. 在 Supabase Dashboard 中，点击左侧菜单的 **SQL Editor**
2. 点击 **New Query**
3. 复制 `supabase_setup.sql` 文件中的全部内容
4. 粘贴到 SQL Editor 中
5. 点击 **Run** 执行 SQL 脚本
6. 确认看到 "Success. No rows returned" 或类似成功消息

### 1.3 创建 Storage Bucket

1. 在 Supabase Dashboard 中，点击左侧菜单的 **Storage**
2. 点击 **Create a new bucket**
3. 填写信息：
   - **Name**: `journal-images`
   - **Public bucket**: ✅ **勾选**（这样图片才能公开访问）
4. 点击 **Create bucket**
5. 点击 bucket 名称进入详情页
6. 点击 **Policies** 标签
7. 点击 **New Policy**，选择 **For full customization**
8. 使用以下策略（允许所有人读取，但只有认证用户写入）：

```sql
-- 允许所有人读取
CREATE POLICY "Public Access" ON storage.objects
FOR SELECT USING (bucket_id = 'journal-images');

-- 允许认证用户上传（如果需要，可以改为允许所有人）
CREATE POLICY "Authenticated users can upload" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'journal-images');
```

或者，如果这是个人项目，可以创建更宽松的策略：

```sql
-- 允许所有人读写（个人项目）
CREATE POLICY "Public Access" ON storage.objects
FOR ALL USING (bucket_id = 'journal-images');
```

### 1.4 获取 Supabase 凭证

1. 在 Supabase Dashboard 中，点击左侧菜单的 **Settings** → **API**
2. 找到以下信息并**保存**：
   - **Project URL**: `https://xxxxx.supabase.co`（这是 `SUPABASE_URL`）
   - **anon public key**: `eyJ...`（这是 `SUPABASE_KEY`）

---

## 🚀 第二步：准备代码仓库

### 2.1 创建 GitHub 仓库

1. 登录 GitHub
2. 点击右上角 **+** → **New repository**
3. 填写信息：
   - **Repository name**: `MoodJournal`
   - **Visibility**: Public 或 Private（根据你的需求）
4. 点击 **Create repository**

### 2.2 推送代码到 GitHub

在本地项目目录执行：

```bash
# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: MoodJournal with Supabase support"

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/MoodJournal.git

# 推送代码
git branch -M main
git push -u origin main
```

---

## 🌐 第三步：部署到 Vercel

### 3.1 导入项目

1. 登录 Vercel Dashboard
2. 点击 **Add New...** → **Project**
3. 选择 **Import Git Repository**
4. 选择你的 GitHub 仓库 `MoodJournal`
5. 点击 **Import**

### 3.2 配置项目

在项目配置页面：

1. **Framework Preset**: 选择 **Other** 或留空
2. **Root Directory**: 留空（或填写 `./`）
3. **Build Command**: 留空（Streamlit 不需要构建）
4. **Output Directory**: 留空
5. **Install Command**: `pip install -r requirements.txt`

### 3.3 设置环境变量

在 **Environment Variables** 部分，添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SUPABASE_URL` | `https://xxxxx.supabase.co` | 你的 Supabase Project URL |
| `SUPABASE_KEY` | `eyJ...` | 你的 Supabase anon public key |
| `ARK_API_KEY` | `你的火山方舟API密钥` | （可选）AI 生图功能需要 |

### 3.4 部署

1. 点击 **Deploy**
2. 等待部署完成（约 2-3 分钟）
3. 部署成功后，Vercel 会提供一个 URL，如：`https://moodjournal.vercel.app`

---

## ✅ 第四步：验证部署

1. 访问 Vercel 提供的 URL
2. 尝试创建一篇新日记
3. 检查 Supabase Dashboard：
   - **Table Editor** → `journals` 表，应该能看到新记录
   - **Storage** → `journal-images` bucket，应该能看到上传的图片

---

## 🔧 常见问题

### Q: 部署后无法访问？
A: 检查 Vercel 的部署日志，确认环境变量已正确设置。

### Q: 图片无法显示？
A: 
1. 检查 Supabase Storage bucket 是否为 **Public**
2. 检查 Storage Policies 是否正确设置
3. 检查图片 URL 是否可访问

### Q: 数据库连接失败？
A:
1. 检查 `SUPABASE_URL` 和 `SUPABASE_KEY` 是否正确
2. 检查 Supabase 项目是否正常运行
3. 检查网络连接（某些地区可能需要代理）

### Q: AI 生图功能不可用？
A: 
1. 检查 `ARK_API_KEY` 是否已设置
2. 检查 API 密钥是否有效
3. 应用会自动降级到默认背景，不影响核心功能

---

## 📝 本地开发

如果你想在本地测试 Supabase 集成：

1. 创建 `.env` 文件（如果还没有）：
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJ...
ARK_API_KEY=你的API密钥
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
streamlit run app.py
```

---

## 🎉 完成！

现在你的 MoodJournal 已经部署到云端了！可以随时随地访问你的情绪手账本。

**提示**：
- Vercel 提供免费额度，对于个人项目通常足够使用
- Supabase 免费层提供 500MB 数据库和 1GB 存储空间
- 如果数据量增长，可以考虑升级到付费计划

---

## 📚 相关链接

- [Supabase 文档](https://supabase.com/docs)
- [Vercel 文档](https://vercel.com/docs)
- [Streamlit 部署指南](https://docs.streamlit.io/deploy)

