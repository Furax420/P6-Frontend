# Construire les fichiers du site avec Node.js.
FROM node:22-alpine AS build

WORKDIR /app

# Copier d'abord les dépendances pour profiter du cache Docker.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Servir uniquement le résultat du build avec Nginx.
FROM nginx:alpine AS runtime

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist/ /app/

EXPOSE 80
