# ui/Dockerfile

# Stage 1: build the React app
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . ./
RUN npm run build

# Stage 2: serve with nginx on port 8080
FROM nginx:1.23-alpine

# 1) Set the PORT environment variable :contentReference[oaicite:1]{index=1}
ENV PORT 8080

# 2) Replace NGINX default listen 80 with 8080
RUN sed -i 's/listen       80;/listen       8080;/' /etc/nginx/conf.d/default.conf

# 3) Remove default site assets and copy built files
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/build /usr/share/nginx/html

# 4) Expose port 8080 for Cloud Run’s probe :contentReference[oaicite:2]{index=2}
EXPOSE 8080

# 5) Start NGINX
CMD ["nginx", "-g", "daemon off;"]
