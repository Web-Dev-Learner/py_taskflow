# ---------- Base Stage (shared) ----------
FROM node:22-alpine AS base
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install

# ---------- Development Stage ----------
FROM base AS dev
COPY ./frontend .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ---------- Production Build Stage ----------
FROM base AS build
COPY ./frontend .
RUN npm run build

# ---------- Production Server Stage ----------
FROM nginx:alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
