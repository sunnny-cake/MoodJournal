# GitHub 推送代码详细指南

## 📋 前置准备

1. **GitHub 账号**：如果没有，访问 https://github.com 注册
2. **Git 已安装**：Windows 用户通常已安装，如果没有，下载：https://git-scm.com/downloads

---

## 🔧 第一步：检查 Git 状态

### 1.1 打开终端/命令行

- **Windows**: 按 `Win + R`，输入 `cmd` 或 `powershell`，回车
- **或者**：在项目文件夹中，按住 `Shift` 右键，选择 "在此处打开 PowerShell 窗口"

### 1.2 进入项目目录

```bash
cd D:\MoodJournal
```

### 1.3 检查 Git 是否已初始化

```bash
git status
```

**情况 A**：如果看到类似 "fatal: not a git repository" 的错误
→ 说明还没有初始化 Git，继续到 **第二步**

**情况 B**：如果看到文件列表或 "nothing to commit"
→ 说明已经初始化，跳到 **第三步**

---

## 🚀 第二步：初始化 Git（如果还没初始化）

### 2.1 初始化仓库

```bash
git init
```

应该看到：`Initialized empty Git repository in D:/MoodJournal/.git/`

### 2.2 配置 Git 用户信息（如果还没配置）

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

例如：
```bash
git config --global user.name "张三"
git config --global user.email "zhangsan@example.com"
```

**注意**：只需要配置一次，之后所有项目都会使用这个配置。

---

## 📝 第三步：添加文件到 Git

### 3.1 查看当前状态

```bash
git status
```

应该能看到所有未跟踪的文件（红色显示）

### 3.2 添加所有文件

```bash
git add .
```

**说明**：
- `.` 表示当前目录下的所有文件
- 根据 `.gitignore` 规则，`.env` 和 `data/` 文件夹不会被添加（这是正确的，因为它们包含敏感信息）

### 3.3 验证文件已添加

```bash
git status
```

现在应该看到文件变成绿色（已暂存）

---

## 💾 第四步：提交代码

### 4.1 创建提交

```bash
git commit -m "Add Supabase cloud database support"
```

**说明**：
- `-m` 后面是提交信息，描述这次提交做了什么
- 可以改成任何你喜欢的描述，例如：
  - `"Initial commit"`
  - `"添加云端数据库支持"`
  - `"Deploy to cloud"`

### 4.2 验证提交成功

```bash
git log
```

应该能看到刚才的提交记录

---

## 🌐 第五步：创建 GitHub 仓库

### 5.1 登录 GitHub

1. 访问 https://github.com
2. 登录你的账号

### 5.2 创建新仓库

1. 点击右上角的 **+** 图标
2. 选择 **New repository**

### 5.3 填写仓库信息

- **Repository name**: `MoodJournal`（或你喜欢的名字）
- **Description**: `情绪手账本 - Mood Journal App`（可选）
- **Visibility**: 
  - **Public**：所有人都能看到代码（推荐，免费）
  - **Private**：只有你能看到（需要付费账号）
- **不要勾选**：
  - ❌ Initialize this repository with a README
  - ❌ Add .gitignore
  - ❌ Choose a license
  （因为我们已经有了这些文件）

### 5.4 创建仓库

点击 **Create repository**

---

## 🔗 第六步：连接本地仓库和 GitHub

### 6.1 复制仓库 URL

创建仓库后，GitHub 会显示一个页面，上面有仓库的 URL，类似：
```
https://github.com/你的用户名/MoodJournal.git
```

**复制这个 URL**

### 6.2 添加远程仓库

在命令行中执行（**替换 `YOUR_USERNAME` 为你的 GitHub 用户名**）：

```bash
git remote add origin https://github.com/YOUR_USERNAME/MoodJournal.git
```

例如，如果你的用户名是 `zhangsan`：
```bash
git remote add origin https://github.com/zhangsan/MoodJournal.git
```

### 6.3 验证远程仓库已添加

```bash
git remote -v
```

应该能看到：
```
origin  https://github.com/YOUR_USERNAME/MoodJournal.git (fetch)
origin  https://github.com/YOUR_USERNAME/MoodJournal.git (push)
```

---

## 📤 第七步：推送代码到 GitHub

### 7.1 设置默认分支（如果还没设置）

```bash
git branch -M main
```

### 7.2 推送代码

```bash
git push -u origin main
```

**说明**：
- `-u` 表示设置上游分支，之后可以直接用 `git push`
- `origin` 是远程仓库的别名
- `main` 是分支名

### 7.3 输入认证信息

如果提示输入用户名和密码：

**方法 1：使用 Personal Access Token（推荐）**

1. GitHub 不再支持密码登录，需要使用 Personal Access Token
2. 访问：https://github.com/settings/tokens
3. 点击 **Generate new token** → **Generate new token (classic)**
4. 填写：
   - **Note**: `MoodJournal Push`
   - **Expiration**: 选择过期时间（或 No expiration）
   - **Select scopes**: 勾选 `repo`（全部权限）
5. 点击 **Generate token**
6. **复制生成的 token**（只显示一次！）
7. 在命令行中：
   - **Username**: 输入你的 GitHub 用户名
   - **Password**: 粘贴刚才复制的 token（不是密码！）

**方法 2：使用 GitHub Desktop（更简单）**

1. 下载 GitHub Desktop：https://desktop.github.com
2. 登录 GitHub 账号
3. 在 GitHub Desktop 中打开项目
4. 点击 **Publish repository** 按钮

### 7.4 验证推送成功

推送成功后，刷新 GitHub 仓库页面，应该能看到所有代码文件！

---

## ✅ 完成！

现在你的代码已经推送到 GitHub 了！

**下一步**：在 Vercel 中导入这个 GitHub 仓库进行部署。

---

## 🔄 后续更新代码

如果之后修改了代码，只需要：

```bash
# 1. 查看修改
git status

# 2. 添加修改的文件
git add .

# 3. 提交
git commit -m "描述你的修改"

# 4. 推送
git push
```

---

## ❓ 常见问题

### Q: 提示 "remote origin already exists"？
A: 说明已经添加过远程仓库了，可以：
```bash
# 查看现有的远程仓库
git remote -v

# 如果需要修改，先删除再添加
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/MoodJournal.git
```

### Q: 提示 "failed to push some refs"？
A: 可能是 GitHub 仓库有文件而本地没有，执行：
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Q: 忘记添加 `.env` 文件，已经推送到 GitHub 了？
A: 不用担心，`.env` 在 `.gitignore` 中，不会被推送。如果担心，可以检查 GitHub 仓库中是否有 `.env` 文件。

### Q: 想删除 GitHub 上的某个文件？
A: 在本地删除文件后：
```bash
git add .
git commit -m "删除文件"
git push
```

