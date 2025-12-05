# MoodJournal 快速部署指南

## 🚀 5分钟快速部署

### 步骤 1: 设置 Supabase（2分钟）

1. 访问 https://supabase.com 注册并创建新项目
2. 在 **SQL Editor** 中执行 `supabase_setup.sql` 的内容
3. 在 **Storage** 中创建名为 `journal-images` 的 **Public** bucket
4. 在 **Settings → API** 中复制：
   - `SUPABASE_URL`（Project URL）
   - `SUPABASE_KEY`（anon public key）

### 步骤 2: 推送代码到 GitHub（1分钟）

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/MoodJournal.git
git push -u origin main
```

### 步骤 3: 部署到 Vercel（2分钟）

1. 访问 https://vercel.com，使用 GitHub 登录
2. 点击 **Add New Project** → 选择你的仓库
3. 在 **Environment Variables** 中添加：
   - `SUPABASE_URL` = 你的 Supabase URL
   - `SUPABASE_KEY` = 你的 Supabase Key
   - `ARK_API_KEY` = 你的火山方舟 API 密钥（可选）
4. 点击 **Deploy**

### ✅ 完成！

访问 Vercel 提供的 URL，开始使用你的云端手账本！

---

## 📝 详细说明

完整部署指南请查看 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## 🔧 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件
echo "SUPABASE_URL=你的URL" > .env
echo "SUPABASE_KEY=你的KEY" >> .env
echo "ARK_API_KEY=你的API密钥" >> .env

# 运行
streamlit run app.py
```

