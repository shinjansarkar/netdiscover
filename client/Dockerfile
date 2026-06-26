# Multi-stage production build for Next.js
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies first for layer caching
COPY package.json package-lock.json* ./
RUN npm ci

# Copy all source code
COPY . .

# Next.js embeds NEXT_PUBLIC_ variables at build time, so we must pass them as ARGs during the build phase
ARG NEXT_PUBLIC_API_KEY
ARG NEXT_PUBLIC_API_BASE_URL

ENV NEXT_PUBLIC_API_KEY=$NEXT_PUBLIC_API_KEY
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

# Build the production application
RUN npm run build

# --- Runner Stage ---
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copy built assets and dependencies from builder stage
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

# Start the Next.js production server
CMD ["npm", "start"]
