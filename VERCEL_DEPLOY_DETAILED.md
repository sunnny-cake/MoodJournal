# ⚠️ 重要提示：Vercel 不支持 Streamlit 应用

## 🚨 问题说明

**Vercel 无法直接部署 Streamlit 应用**，因为：
- Streamlit 需要持续运行的服务器进程
- Vercel 是无服务器平台，只支持静态网站和 API 函数
- 这就是为什么你会看到 404 错误

## ✅ 推荐解决方案

### 方案 1：Streamlit Cloud（强烈推荐）⭐

**最简单、最稳定、完全免费**

- ✅ Streamlit 官方提供的部署平台
- ✅ 专为 Streamlit 应用设计
- ✅ 一键部署，自动更新
- ✅ 完全免费

**详细指南**：请查看 `STREAMLIT_CLOUD_DEPLOY.md`

### 方案 2：Railway（备选）

**支持 Python 应用，简单易用**

- ✅ 完美支持 Streamlit
- ✅ 每月 $5 免费额度
- ✅ 连接 GitHub 自动部署

**详细指南**：请查看 `RAILWAY_DEPLOY.md`

---

## 📋 以下内容仅供参考（Vercel 配置说明）

**注意**：以下配置无法让 Streamlit 在 Vercel 上正常运行，仅供参考。

---

## 📋 前置准备

在开始之前，确保你已经完成：
- ✅ Supabase 数据库和 Storage bucket 已设置
- ✅ 已获取 `SUPABASE_URL` 和 `SUPABASE_KEY`
- ✅ 代码已推送到 GitHub 仓库

---

## 🚀 第一步：创建 Vercel 账号

### 1.1 访问 Vercel

1. 访问 https://vercel.com
2. 点击右上角的 **Sign Up**

### 1.2 选择登录方式

**推荐方式：使用 GitHub 登录**
1. 点击 **Continue with GitHub**
2. 授权 Vercel 访问你的 GitHub 账号
3. 填写基本信息（如果需要）

**其他方式**：
- 也可以使用邮箱注册，但使用 GitHub 登录更方便（可以直接导入仓库）

---

## 📦 第二步：导入 GitHub 仓库

### 2.1 进入导入页面

1. 登录 Vercel 后，点击右上角的 **Add New...**
2. 选择 **Project**

### 2.2 选择仓库

1. 在 **Import Git Repository** 页面，你应该能看到你的 GitHub 仓库列表
2. 找到 `MoodJournal` 仓库（或你创建时使用的名字）
3. 点击 **Import** 按钮

**如果没有看到仓库**：
- 点击 **Adjust GitHub App Permissions**
- 确保授权了仓库访问权限
- 或者点击 **Import** 旁边的下拉菜单，选择 **Import from GitHub**

---

## ⚙️ 第三步：配置项目设置

### 3.1 项目配置页面

导入仓库后，会进入项目配置页面。需要设置以下内容：

#### Framework Preset
- **选择**: `Other` 或留空
- Streamlit 不是 Vercel 官方支持的框架，所以选择 Other

#### Root Directory
- **留空**（或填写 `./`）
- 如果你的项目在子目录，填写子目录路径

#### Build and Output Settings

**Build Command**:
- **留空**（Streamlit 不需要构建步骤）

**Output Directory**:
- **留空**

**Install Command**:
- 填写：`pip install -r requirements.txt`
- 这会告诉 Vercel 安装 Python 依赖

### 3.2 环境变量设置（重要！）

这是最关键的一步！

#### 添加环境变量

在 **Environment Variables** 部分，点击 **Add** 按钮，逐个添加以下变量：

**1. SUPABASE_URL**
- **Name**: `SUPABASE_URL`
- **Value**: 你的 Supabase Project URL（格式：`https://xxxxx.supabase.co`）
- **Environment**: 选择所有环境（Production, Preview, Development）

**2. SUPABASE_KEY**
- **Name**: `SUPABASE_KEY`
- **Value**: 你的 Supabase anon public key（很长的一串）
- **Environment**: 选择所有环境

**3. ARK_API_KEY**（可选，如果使用 AI 生图功能）
- **Name**: `ARK_API_KEY`
- **Value**: 你的火山方舟 API 密钥
- **Environment**: 选择所有环境

#### 验证环境变量

添加完所有环境变量后，应该能看到：
```
SUPABASE_URL = https://xxxxx.supabase.co
SUPABASE_KEY = eyJ...
ARK_API_KEY = xxx...（如果添加了）
```

⚠️ **重要提示**：
- 确保环境变量名称**完全一致**（区分大小写）
- 确保值**没有多余的空格**
- 如果复制粘贴，注意不要复制到换行符

---

## 🚀 第四步：部署项目

### 4.1 开始部署

1. 确认所有配置都正确
2. 点击页面底部的 **Deploy** 按钮

### 4.2 等待部署

部署过程通常需要 2-5 分钟，你会看到：
1. **Building** - 安装依赖和构建（Streamlit 会跳过构建）
2. **Deploying** - 部署到 Vercel 服务器

**部署日志示例**：
```
Cloning repository...
Installing dependencies...
pip install -r requirements.txt
...
Deploying...
```

### 4.3 部署成功

部署成功后，你会看到：
- ✅ **Congratulations!** 消息
- 一个 URL，格式类似：`https://moodjournal-xxxxx.vercel.app`
- 或者自定义域名（如果配置了）

---

## ⚠️ 第五步：修复 Streamlit 配置（重要！）

**问题**：Vercel 默认不支持 Streamlit，需要特殊配置。

### 5.1 创建 `vercel.json` 配置文件

如果项目中还没有 `vercel.json`，需要创建一个：

**文件位置**：项目根目录 `vercel.json`

**文件内容**：
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "STREAMLIT_SERVER_PORT": "8080",
    "STREAMLIT_SERVER_ADDRESS": "0.0.0.0"
  }
}
```

### 5.2 如果已有 vercel.json

检查 `vercel.json` 文件内容是否正确，确保包含上述配置。

### 5.3 重新部署

1. 如果修改了 `vercel.json`，需要重新部署：
   - 在 Vercel Dashboard，点击项目
   - 点击 **Deployments** 标签
   - 点击最新的部署右侧的 **...** 菜单
   - 选择 **Redeploy**

2. 或者推送代码到 GitHub（会自动触发重新部署）：
   ```bash
   git add vercel.json
   git commit -m "Add Vercel configuration"
   git push
   ```

---

## 🔧 第六步：配置 Streamlit（如果部署失败）

### 6.1 创建 `Procfile`（可选）

如果 Vercel 部署有问题，可以尝试创建 `Procfile`：

**文件位置**：项目根目录 `Procfile`

**文件内容**：
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### 6.2 创建 `runtime.txt`（可选）

指定 Python 版本：

**文件位置**：项目根目录 `runtime.txt`

**文件内容**：
```
python-3.11
```

---

## ✅ 第七步：验证部署

### 7.1 访问应用

1. 在 Vercel Dashboard，点击项目
2. 点击 **Visit** 按钮，或直接访问部署 URL
3. 应该能看到 MoodJournal 应用界面

### 7.2 测试功能

1. **创建新日记**：
   - 填写日期、天气、文字
   - 上传图片（可选）
   - 点击"生成手帐"
   - 应该能成功生成并保存

2. **检查数据库**：
   - 在 Supabase Dashboard → Table Editor → `journals`
   - 应该能看到新创建的记录

3. **检查图片存储**：
   - 在 Supabase Dashboard → Storage → `journal-images`
   - 应该能看到上传的图片

### 7.3 查看日志（如果出错）

如果应用无法正常运行：

1. 在 Vercel Dashboard，点击项目
2. 点击 **Deployments** 标签
3. 点击最新的部署
4. 查看 **Logs** 标签，检查错误信息

**常见错误**：
- `ModuleNotFoundError`: 缺少依赖，检查 `requirements.txt`
- `Environment variable not set`: 环境变量未设置，检查 Environment Variables
- `Connection refused`: Supabase 连接问题，检查 URL 和 KEY

---

## 🌐 第八步：配置自定义域名（可选）

### 8.1 添加域名

1. 在 Vercel Dashboard，点击项目
2. 点击 **Settings** → **Domains**
3. 输入你的域名（例如：`moodjournal.com`）
4. 点击 **Add**

### 8.2 配置 DNS

按照 Vercel 的提示配置 DNS 记录：
- 添加 CNAME 记录指向 Vercel
- 或添加 A 记录指向 Vercel IP

---

## 🔄 后续更新

### 自动部署

Vercel 会自动监听 GitHub 仓库的变化：
- 当你推送代码到 GitHub 时，Vercel 会自动重新部署
- 在 **Deployments** 页面可以看到所有部署历史

### 手动重新部署

1. 在 Vercel Dashboard，点击项目
2. 点击 **Deployments** 标签
3. 点击某个部署右侧的 **...** 菜单
4. 选择 **Redeploy**

### 回滚到之前的版本

1. 在 **Deployments** 页面
2. 找到之前的成功部署
3. 点击右侧的 **...** 菜单
4. 选择 **Promote to Production**

---

## ❓ 常见问题

### Q: 部署后显示 "404 Not Found"？

**A**: 检查 `vercel.json` 配置是否正确，确保路由配置正确。

**解决方案**：
1. 确认 `vercel.json` 文件存在且内容正确
2. 重新部署项目

### Q: 应用无法连接 Supabase？

**A**: 检查环境变量是否正确设置。

**解决方案**：
1. 在 Vercel Dashboard → Settings → Environment Variables
2. 确认 `SUPABASE_URL` 和 `SUPABASE_KEY` 已设置
3. 确认值正确（没有多余空格）
4. 重新部署

### Q: 图片无法显示？

**A**: 检查 Supabase Storage bucket 权限。

**解决方案**：
1. 确认 `journal-images` bucket 是 **Public**
2. 检查 Storage Policies 是否正确设置
3. 在 Supabase Dashboard 测试图片 URL 是否可访问

### Q: 部署时间太长？

**A**: 首次部署需要安装所有依赖，可能需要几分钟。

**解决方案**：
- 耐心等待（通常 2-5 分钟）
- 如果超过 10 分钟，检查日志是否有错误

### Q: 如何查看实时日志？

**A**: 在部署页面查看 Logs。

**步骤**：
1. Vercel Dashboard → 项目 → Deployments
2. 点击最新的部署
3. 查看 **Logs** 标签

### Q: 如何更新环境变量？

**A**: 在 Settings 中修改。

**步骤**：
1. Vercel Dashboard → 项目 → Settings → Environment Variables
2. 修改或添加变量
3. 重新部署（修改环境变量后需要重新部署才能生效）

### Q: Streamlit 应用在 Vercel 上运行缓慢？

**A**: Vercel 的免费计划有冷启动时间。

**解决方案**：
- 这是正常的，首次访问可能需要几秒钟启动
- 后续访问会更快（应用保持运行状态）
- 考虑升级到付费计划以获得更好的性能

---

## 🎉 完成！

恭喜！你的 MoodJournal 应用已经成功部署到 Vercel 了！

现在你可以：
- ✅ 随时随地访问你的手账本
- ✅ 在手机上使用（响应式设计）
- ✅ 数据存储在云端（Supabase）
- ✅ 自动备份（GitHub + Supabase）

**下一步**：
- 分享给你的朋友使用
- 继续优化功能和样式
- 添加更多功能（标签、搜索、导出等）

---

## 📚 相关资源

- [Vercel 文档](https://vercel.com/docs)
- [Streamlit 部署指南](https://docs.streamlit.io/deploy)
- [Supabase 文档](https://supabase.com/docs)

