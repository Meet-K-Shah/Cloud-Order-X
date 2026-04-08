FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --quiet
COPY . .
RUN npx ng build --configuration production

FROM nginx:1.25-alpine
COPY --from=builder /app/dist/cloudorderx /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
