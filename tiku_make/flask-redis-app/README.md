# Flask Redis App

这是一个使用Flask和Redis构建的简单Web应用程序，提供用户身份验证和Redis操作的功能。

## 项目结构

```
flask-redis-app
├── src
│   ├── app.py          # 应用程序入口点
│   ├── auth.py         # 身份验证相关功能
│   ├── redis_client.py  # Redis数据库操作
│   └── templates
│       └── index.html  # HTML模板
├── requirements.txt     # 项目依赖
└── README.md            # 项目文档
```

## 安装

1. 克隆该项目：

   ```
   git clone <repository-url>
   cd flask-redis-app
   ```

2. 创建并激活虚拟环境（可选）：

   ```
   python -m venv venv
   source venv/bin/activate  # 在Linux或MacOS上
   venv\Scripts\activate     # 在Windows上
   ```

3. 安装依赖：

   ```
   pip install -r requirements.txt
   ```

## 配置

在运行应用程序之前，请确保您已安装并运行Redis服务器。您可以使用默认配置，或根据需要修改`src/redis_client.py`中的连接设置。

## 运行应用程序

在终端中运行以下命令启动Flask应用：

```
python src/app.py
```

应用程序将默认在`http://127.0.0.1:5000`上运行。

## 使用

访问`http://127.0.0.1:5000`以查看应用程序界面。您可以注册新用户并进行登录，以体验身份验证功能。

## 贡献

欢迎任何形式的贡献！请提交问题或拉取请求。

## 许可证

此项目采用MIT许可证。有关详细信息，请参阅LICENSE文件。