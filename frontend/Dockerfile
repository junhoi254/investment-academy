FROM node:18-alpine

WORKDIR /app

# 패키지 설치
COPY package*.json ./
RUN npm install

# 앱 코드 복사
COPY . .

# 포트 노출
EXPOSE 3000

# 실행
CMD ["npm", "start"]

# 프로덕션 빌드를 위한 멀티 스테이지
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Nginx로 서빙
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
