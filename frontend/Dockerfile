# 基于官方 Node 镜像
FROM node:20

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制所有前端代码
COPY . .

# 构建静态资源
RUN npm run build

# 安装 serve
RUN npm install -g serve

# 暴露端口（关键：这会让 Docker Desktop 自动识别端口）
EXPOSE 3000

# 启动命令：强制指定端口 3000，并指向 dist 目录
CMD ["serve", "-s", "dist", "-l", "3000"]
