FROM node:22-alpine

WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund
COPY bot.mjs ./

USER node
CMD ["node", "bot.mjs"]
