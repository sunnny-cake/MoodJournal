# Railway 部署指南（备选方案）

## 🎯 为什么选择 Railway？

- ✅ **支持 Python 应用**：完美支持 Streamlit
- ✅ **简单易用**：连接 GitHub 即可部署
- ✅ **免费额度**：每月 $5 免费额度（足够个人项目）
- ✅ **自动部署**：推送代码自动更新

---

## 🚀 第一步：注册 Railway

1. 访问 https://railway.app
2. 点击 **Start a New Project**
3. 使用 **GitHub 账号登录**（推荐）

---

## 📦 第二步：创建项目

### 2.1 从 GitHub 导入

1. 选择 **Deploy from GitHub repo**
2. 选择你的 `MoodJournal` 仓库
3. 点击 **Deploy Now**

### 2.2 Railway 会自动检测

Railway 会自动检测到：
- Python 项目
- `requirements.txt`
- `app.py`

---

## ⚙️ 第三步：配置项目

### 3.1 设置启动命令

Railway 可能需要手动设置启动命令：

1. 点击项目 → **Settings**
2. 找到 **Start Command**
3. 填写：
   ```
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

### 3.2 设置环境变量

1. 点击项目 → **Variables**
2. 添加以下环境变量：

| 变量名 | 值 |
|--------|-----|
| `SUPABASE_URL` | `https://xxxxx.supabase.co` |
| `SUPABASE_KEY` | `eyJ...` |
| `ARK_API_KEY` | `xxx...`（可选）|

---

## 🚀 第四步：部署

Railway 会自动开始部署：
1. 安装依赖
2. 启动应用
3. 生成公共 URL

---

## ✅ 第五步：访问应用

部署成功后：
1. Railway 会提供一个公共 URL
2. 格式类似：`https://moodjournal-production.up.railway.app`
3. 点击 URL 访问应用

---

## 🔄 自动更新

Railway 会自动监听 GitHub：
- 推送代码到 GitHub 时自动重新部署
- 在 **Deployments** 标签可以看到部署历史

---

## 💰 费用说明

- **免费额度**：每月 $5（足够个人项目使用）
- **超出后**：按使用量付费
- **个人项目**：通常不会超出免费额度

---

## ❓ 常见问题

### Q: 如何查看日志？
A: 在项目页面点击 **View Logs**

### Q: 如何自定义域名？
A: 在 Settings → Domains 中添加自定义域名

### Q: 如何暂停应用？
A: 在 Settings 中可以暂停应用（节省额度）

---

## 📚 相关资源

- [Railway 文档](https://docs.railway.app)
- [Railway 官网](https://railway.app)

