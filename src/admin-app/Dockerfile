# ============================================================================
# SkillSynth Admin — SvelteKit adapter-node Dockerfile
# ============================================================================

# --- Stage 1: Dependencies ---
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN corepack enable pnpm && \
    pnpm install --frozen-lockfile

# --- Stage 2: Build ---
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY svelte.config.js vite.config.ts tsconfig.json ./
COPY src ./src
COPY static ./static

ARG PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api
ENV PUBLIC_API_BASE_URL=$PUBLIC_API_BASE_URL

RUN corepack enable pnpm && \
    pnpm build

# --- Stage 3: Runtime (adapter-node server) ---
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nodejs

COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules

USER nodejs

ENV PORT=3001
ENV HOST=0.0.0.0

EXPOSE 3001

CMD ["node", "build"]
