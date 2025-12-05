# AI生图功能配置说明

## 功能说明

MoodJournal 现在支持使用火山方舟AI生成Dreamcore风格的手账背景！

## 安装依赖

首先需要安装火山方舟SDK：

```bash
pip install 'volcengine-python-sdk[ark]'
```

同时确保已安装 `requests` 库（通常已包含在Streamlit中）：

```bash
pip install requests
```

## 配置API密钥

1. 获取API Key：
   - 访问：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
   - 创建或复制你的API Key

2. 设置环境变量：

   **Windows (PowerShell):**
   ```powershell
   $env:ARK_API_KEY="你的API密钥"
   ```

   **Windows (CMD):**
   ```cmd
   set ARK_API_KEY=你的API密钥
   ```

   **macOS/Linux:**
   ```bash
   export ARK_API_KEY="你的API密钥"
   ```

   **永久设置（推荐）：**
   - Windows: 在系统环境变量中添加 `ARK_API_KEY`
   - macOS/Linux: 在 `~/.bashrc` 或 `~/.zshrc` 中添加 `export ARK_API_KEY="你的API密钥"`

## 使用方法

1. 配置好API密钥后，启动应用
2. 在"新建日记"页面输入文字、选择日期和天气
3. 点击"生成手账"，系统会自动：
   - 根据你的输入生成AI背景（如果API可用）
   - 如果AI不可用或失败，自动降级使用默认背景
   - 保留所有原有的图片处理和文字排版功能

## 降级机制

- 如果未安装SDK：自动使用默认背景
- 如果API密钥未设置：自动使用默认背景
- 如果API调用失败：自动使用默认背景
- 所有情况下，用户图片和文字排版功能都正常工作

## 成本说明

- 使用火山方舟的免费额度（50万token）
- 每次生成背景图大约消耗一定token
- 建议监控使用量，避免超出免费额度

## 故障排查

1. **AI功能不工作？**
   - 检查是否安装了SDK：`pip list | grep volcengine`
   - 检查环境变量：`echo $ARK_API_KEY` (Linux/Mac) 或 `echo %ARK_API_KEY%` (Windows)
   - 查看应用日志，看是否有错误信息

2. **生成速度慢？**
   - AI生图通常需要5-30秒，这是正常的
   - 如果超时，会自动降级使用默认背景

3. **想禁用AI功能？**
   - 不设置 `ARK_API_KEY` 环境变量即可
   - 或者修改代码中 `create_journal_page` 的 `use_ai=False` 参数

