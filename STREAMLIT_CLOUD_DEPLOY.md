# Streamlit Cloud 部署指南（推荐方案）

## 🎯 为什么选择 Streamlit Cloud？

- ✅ **官方支持**：Streamlit 官方提供的免费部署平台
- ✅ **一键部署**：连接 GitHub 仓库即可自动部署
- ✅ **完全免费**：个人项目完全免费
- ✅ **自动更新**：推送代码到 GitHub 自动重新部署
- ✅ **完美支持**：专为 Streamlit 应用设计

---

## 🚀 第一步：准备 GitHub 仓库

确保你的代码已经推送到 GitHub（你应该已经完成了）：
- ✅ 代码在 GitHub 上
- ✅ 包含 `requirements.txt`
- ✅ 包含 `app.py`

---

## 📦 第二步：访问 Streamlit Cloud

1. 访问 https://streamlit.io/cloud
2. 点击 **Sign up** 或 **Get started**
3. 使用 **GitHub 账号登录**（推荐）

---

## 🔗 第三步：授权 GitHub

1. 点击 **Authorize Streamlit Cloud**
2. 授权 Streamlit Cloud 访问你的 GitHub 仓库
3. 选择仓库访问权限：
   - **All repositories**（推荐，方便）
   - 或 **Only select repositories**（更安全）

---

## 🚀 第四步：部署应用

### 4.1 创建新应用

1. 登录后，点击 **New app**
2. 填写应用信息：

**Repository（仓库）**：
- 选择你的 `MoodJournal` 仓库

**Branch（分支）**：
- 选择 `main`（或你的主分支）

**Main file path（主文件路径）**：
- 填写：`app.py`

**App URL（应用URL，可选）**：
- 可以自定义，例如：`moodjournal`
- 最终 URL：`https://moodjournal.streamlit.app`

### 4.2 配置环境变量

在部署前，点击 **Advanced settings**，添加环境变量：

**添加以下环境变量**：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SUPABASE_URL` | `https://xxxxx.supabase.co` | 你的 Supabase URL |
| `SUPABASE_KEY` | `eyJ...` | 你的 Supabase Key |
| `ARK_API_KEY` | `xxx...` | （可选）AI API 密钥 |

**添加步骤**：
1. 点击 **Secrets** 标签
2. 点击 **New secret**
3. 输入变量名和值
4. 点击 **Save**

### 4.3 开始部署

1. 确认所有配置正确
2. 点击 **Deploy**

---

## ⏳ 第五步：等待部署

部署过程通常需要 1-3 分钟，你会看到：
1. **Building** - 安装依赖
2. **Running** - 启动应用
3. ✅ **Success** - 部署成功

---

## ✅ 第六步：访问应用

部署成功后：
1. 点击 **View app** 按钮
2. 或访问你的应用 URL：`https://你的应用名.streamlit.app`

---

## 🔄 自动更新

Streamlit Cloud 会自动监听 GitHub 仓库：
- 当你推送代码到 GitHub 时，会自动重新部署
- 在应用页面可以看到部署历史和日志

---

## 🔧 查看日志和调试

如果应用有问题：

1. 在 Streamlit Cloud Dashboard，点击你的应用
2. 查看 **Logs** 标签
3. 检查错误信息

**常见问题**：
- `ModuleNotFoundError`: 检查 `requirements.txt` 是否包含所有依赖
- `Environment variable not set`: 检查 Secrets 中是否设置了环境变量

---

## 📝 更新环境变量

1. 在应用页面，点击 **Settings**
2. 点击 **Secrets** 标签
3. 添加、修改或删除环境变量
4. 保存后会自动重新部署

---

## 🎉 完成！

现在你的 MoodJournal 应用已经成功部署到 Streamlit Cloud 了！

**优势**：
- ✅ 完全免费
- ✅ 自动更新
- ✅ 官方支持
- ✅ 稳定可靠

---

## ❓ 常见问题

### Q: 部署失败，提示缺少依赖？
A: 检查 `requirements.txt` 是否包含所有必需的包。

### Q: 应用无法连接 Supabase？
A: 检查 Secrets 中的 `SUPABASE_URL` 和 `SUPABASE_KEY` 是否正确。

### Q: 如何查看实时日志？
A: 在应用页面点击 **Logs** 标签。

### Q: 如何回滚到之前的版本？
A: Streamlit Cloud 会自动保留部署历史，可以在 GitHub 中回滚代码。

---

## 📚 相关资源

- [Streamlit Cloud 文档](https://docs.streamlit.io/streamlit-cloud)
- [Streamlit Cloud 官网](https://streamlit.io/cloud)

