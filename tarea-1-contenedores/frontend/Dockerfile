# 1) Build de la app
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

# 2) Contenedor final: Nginx sirviendo /dist
FROM nginx:1.27-alpine AS runner
COPY --from=build /app/dist /usr/share/nginx/html
# Nginx ya escucha en 80
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
