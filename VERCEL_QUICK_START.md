# Vercel 快速部署指南（5分钟）

## 🚀 快速步骤

### 1. 登录 Vercel（1分钟）
- 访问 https://vercel.com
- 点击 **Sign Up** → **Continue with GitHub**
- 授权 GitHub 账号

### 2. 导入项目（1分钟）
- 点击 **Add New...** → **Project**
- 找到 `MoodJournal` 仓库
- 点击 **Import**

### 3. 配置项目（2分钟）

**项目设置**：
- Framework Preset: `Other`
- Root Directory: 留空
- Build Command: 留空
- Output Directory: 留空
- Install Command: `pip install -r requirements.txt`

**环境变量**（重要！）：
点击 **Environment Variables** → **Add**，添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SUPABASE_URL` | `https://xxxxx.supabase.co` | 你的 Supabase URL |
| `SUPABASE_KEY` | `eyJ...` | 你的 Supabase Key |
| `ARK_API_KEY` | `xxx...` | （可选）AI API 密钥 |

⚠️ **重要**：确保三个环境（Production, Preview, Development）都勾选！

### 4. 部署（1分钟）
- 点击 **Deploy**
- 等待 2-5 分钟
- 看到 ✅ **Congratulations!** 即成功

### 5. 访问应用
- 点击 **Visit** 按钮
- 或访问提供的 URL：`https://moodjournal-xxxxx.vercel.app`

---

## ✅ 验证清单

部署成功后，检查：

- [ ] 应用能正常打开
- [ ] 能创建新日记
- [ ] 图片能上传和显示
- [ ] 数据保存到 Supabase（在 Supabase Dashboard 查看）

---

## 🔧 如果遇到问题

### 404 错误？
→ 检查 `vercel.json` 文件是否存在且正确

### 无法连接数据库？
→ 检查环境变量是否正确设置，重新部署

### 图片无法显示？
→ 检查 Supabase Storage bucket 是否为 Public

---

## 📖 详细说明

完整指南请查看：`VERCEL_DEPLOY_DETAILED.md`

