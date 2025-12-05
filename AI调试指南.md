# 🔍 AI接口调试指南

## 问题排查步骤

### 1. 检查SDK是否安装

运行以下命令检查：
```bash
pip list | findstr volcengine
```

如果没看到 `volcengine-python-sdk`，请安装：
```bash
pip install 'volcengine-python-sdk[ark]'
```

### 2. 检查API密钥是否设置

**方法A：检查.env文件**
- 确认 `D:\MoodJournal\.env` 文件存在
- 确认文件内容格式：`ARK_API_KEY=你的密钥`
- 确认没有多余的空格或引号

**方法B：在代码中临时测试**
在Python中运行：
```python
import os
from dotenv import load_dotenv
load_dotenv()
print("API Key:", os.getenv('ARK_API_KEY'))
```

如果显示 `None`，说明环境变量未正确加载。

### 3. 检查API密钥是否正确

- 访问：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
- 确认密钥是否有效
- 确认密钥有足够的额度

### 4. 查看详细错误信息

现在代码会显示详细的错误信息，包括：
- ⚠️ SDK未安装
- ⚠️ API密钥未设置
- ❌ API调用失败的具体原因
- 💡 针对性的解决建议

### 5. 常见错误及解决方案

#### 错误1：`AI功能不可用：未安装 volcengine-python-sdk[ark]`
**解决：**
```bash
pip install 'volcengine-python-sdk[ark]'
```

#### 错误2：`AI功能不可用：未设置 ARK_API_KEY 环境变量`
**解决：**
1. 在项目根目录创建 `.env` 文件
2. 写入：`ARK_API_KEY=你的真实密钥`
3. 安装：`pip install python-dotenv`
4. 重启应用

#### 错误3：`AI生图失败：api_key invalid` 或类似认证错误
**解决：**
- 检查API密钥是否正确
- 检查密钥是否过期
- 重新生成API密钥

#### 错误4：`AI生图失败：model not found`
**解决：**
- 检查模型ID是否正确：`doubao-seedream-4-5-251128`
- 确认该模型在你的账户中可用

#### 错误5：`图片下载失败：HTTP 403/404`
**解决：**
- 可能是图片URL过期或无效
- 检查网络连接
- 重试生成

### 6. 测试API连接

创建一个测试脚本 `test_ai.py`：

```python
import os
from dotenv import load_dotenv
load_dotenv()

from volcenginesdkarkruntime import Ark

api_key = os.getenv('ARK_API_KEY')
if not api_key:
    print("❌ API密钥未设置")
    exit(1)

print(f"✅ API密钥已加载: {api_key[:10]}...")

try:
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )
    
    print("🎨 正在测试AI生图...")
    response = client.images.generate(
        model="doubao-seedream-4-5-251128",
        prompt="a beautiful dreamcore aesthetic background, soft pastel colors",
        size="2K",
        response_format="url",
        watermark=False
    )
    
    if response.data and len(response.data) > 0:
        print(f"✅ 成功！图片URL: {response.data[0].url}")
    else:
        print("❌ 响应为空")
        
except Exception as e:
    print(f"❌ 错误: {e}")
```

运行测试：
```bash
python test_ai.py
```

### 7. 启用调试模式

如果想看到生成的prompt，可以取消注释代码中的这一行：
```python
# st.info(f"🎨 AI Prompt: {prompt[:100]}...")
```

改为：
```python
st.info(f"🎨 AI Prompt: {prompt[:100]}...")
```

这样可以看到实际发送给AI的提示词。

## 成功标志

如果AI生图成功，你会看到：
- ✨ `AI背景生成成功！` 的成功提示
- 手账背景是AI生成的图片（而不是默认的纸质纹理）

## 降级机制

如果AI生图失败，系统会自动：
- 使用默认的纸质纹理背景
- 保留所有其他功能（图片处理、文字排版等）
- 显示错误信息帮助排查问题

## 需要帮助？

如果以上步骤都无法解决问题，请提供：
1. 具体的错误信息（从应用界面复制）
2. SDK是否安装：`pip list | findstr volcengine`
3. API密钥是否设置：`python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ARK_API_KEY'))"`

