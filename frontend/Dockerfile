# Use a Node.js base image with pnpm pre-installed
FROM node:22-slim AS base

# Install pnpm (if not pre-installed in the image)
RUN corepack enable && corepack prepare pnpm@latest --activate

# ===== Builder Stage (dependencies + build) =====
FROM base AS builder

WORKDIR /app

# Copy package files for dependency installation
COPY package.json pnpm-lock.yaml ./

# Install dependencies (frozen lockfile)
RUN pnpm install --frozen-lockfile

# Copy all source files
COPY . .

# Build the app (if needed for production)
# RUN pnpm build

# ===== Production Stage =====
FROM base AS production

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/pnpm-lock.yaml ./pnpm-lock.yaml

# Copy built files (if using `pnpm build`)
# COPY --from=builder /app/dist ./dist

# Copy source files (for development with HMR)
COPY . .

# Expose the Vite dev server port (default: 5173)
EXPOSE 3000

# Start the Vite dev server (for development)
CMD ["pnpm", "dev", "--host", "0.0.0.0"]