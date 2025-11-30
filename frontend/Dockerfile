# Stage 1: Build Vue app
FROM node:20-bullseye AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --prefer-offline
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# 清理原始静态文件
RUN rm -rf /usr/share/nginx/html/*
# 拷贝前端构建结果
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
# 修改 Dockerfile 复制配置  
COPY ./default.conf /etc/nginx/conf.d/default.conf

