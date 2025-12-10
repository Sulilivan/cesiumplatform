# Cesium Apartment

基于 Vue 3 + Vite + Cesium 的三维地球可视化前端应用，已打包为 Docker 镜像，开箱即用。

## 镜像地址

```
rayansullivan/cesiumapartment:latest
```

## 快速开始

1. **拉取镜像**

   ```sh
   docker pull rayansullivan/cesiumapartment:latest
   ```

2. **运行容器**

   ```sh
   docker run -p 5173:5173 rayansullivan/cesiumapartment:latest
   ```

3. **访问应用**

   打开浏览器访问 [http://localhost:5173](http://localhost:5173)

## 功能简介

- 基于 Cesium 实现三维地球可视化
- 支持 3D Tiles 模型加载
- Vue 3 + Vite 前端架构，易于扩展

## 本地开发

如需本地开发或自定义构建：

```sh
git clone https://github.com/你的仓库地址.git
cd frontend
npm install
npm run dev
```

## 生产构建

```sh
npm run build
```

## 说明

- 镜像已内置所有依赖和静态资源，无需额外配置。
- 默认使用 `serve` 启动生产环境静态服务。

---

如有问题欢迎联系作者或提交 issue。
