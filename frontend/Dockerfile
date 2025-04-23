FROM node:18-alpine

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy package.json and pnpm-lock.yaml
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy the rest of the application
COPY . .

# Build the application
RUN pnpm build

# Expose the port
EXPOSE 3000

# Start the application
CMD ["pnpm", "start"]
