# Phase 1: Build the React app
FROM node:latest as builder
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .

ARG REACT_APP_GEOAPI_BASE_URL
ENV REACT_APP_GEOAPI_BASE_URL=$REACT_APP_GEOAPI_BASE_URL

ARG REACT_APP_RAPIDAPI_KEY
ENV REACT_APP_RAPIDAPI_KEY=$REACT_APP_RAPIDAPI_KEY

RUN npm run build

# Phase 2: Serve the React app with nginx
FROM nginx:alpine as production
COPY --from=builder /usr/src/app/build /usr/share/nginx/html
COPY --from=builder /usr/src/app/nginx/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80