FROM node:20-alpine AS base

WORKDIR /app

# Copy only package.json (not the lockfile). The lockfile contains
# platform-specific optional deps resolved on macOS (darwin), which
# won't include the linux-musl binaries needed by Alpine. A fresh
# npm install inside the container resolves the correct native binaries
# (lightningcss, etc.) for the target platform.
COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
