# ASR测评平台

这是一个用于音频文件管理和ASR（自动语音识别）测评的Web平台。该平台支持音频文件和对应文本的批量上传、管理，并计划支持多个ASR服务商的语音识别评测功能。

## 功能特点

- 支持音频文件批量上传和管理
- 支持标注文本文件的上传和管理
- 音频文件与标注文本的关联管理
- 支持多种ASR服务商（计划中）：
  - 腾讯云
  - 阿里云
  - 讯飞
  - 豆包（字节）
  - 百度
  - 携程
  - Whisper

## 技术栈

- 后端：Python Flask
- 前端：HTML5 + CSS3 + JavaScript
- 数据库：SQLite3
- 依赖管理：pip

## 系统要求

- Python 3.7+
- pip（Python包管理器）
- 现代浏览器（Chrome、Firefox、Safari等）

## 安装部署

1. 克隆项目到本地：
```bash
git clone https://github.com/Nancychen2023/asr_model_evaluate.git
cd asr_model_evaluate
```

2. 创建并激活虚拟环境（推荐）：
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 初始化数据库：
```bash
# 数据库会在首次运行时自动初始化
```

5. 运行应用：
```bash
python app.py
```

6. 访问应用：
打开浏览器访问 `http://localhost:5000`

## 目录结构

```
asr_model_evaluate/
├── app.py              # 主应用程序
├── requirements.txt    # 项目依赖
├── README.md          # 项目说明文档
├── CHANGELOG.md       # 变更日志
├── templates/         # HTML模板文件
│   └── index.html    # 主页面模板
├── uploads/          # 音频文件上传目录
└── text_uploads/     # 文本文件上传目录
```

## 使用说明

1. 音频文件上传
   - 支持批量上传音频文件
   - 可选择音频语种、采样率和声道数
   - 支持查看上传历史记录

2. 文本文件上传
   - 支持批量上传标注文本
   - 支持.txt、.doc、.docx格式
   - 自动与音频文件关联

3. 文件管理
   - 支持查看所有上传的音频和文本文件
   - 支持文件删除操作
   - 支持查看文本内容

4. ASR评测（开发中）
   - 支持选择不同的ASR服务商
   - 支持自定义评测参数
   - 支持查看评测结果

## 注意事项

1. 请确保上传目录（uploads/和text_uploads/）具有适当的写入权限
2. 大文件上传可能需要调整服务器配置
3. 建议定期备份数据库文件

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至：[您的邮箱] 