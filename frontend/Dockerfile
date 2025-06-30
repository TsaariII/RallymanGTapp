FROM node:20.13.1-bookworm-slim

WORKDIR /app

# Copy package files first (for better Docker layer caching)
COPY package*.json ./

# Install project dependencies
RUN npm install

# Install serve globally
RUN npm install -g serve

# Copy source code
COPY . .

# Build the React app (outputs to dist/ directory)
RUN npm run build

# Expose port 9000
EXPOSE 9000

# Serve the built React app
# -s flag enables SPA mode (handles React Router)
# -l flag specifies port
# dist is the build output directory
CMD ["serve", "-s", "dist", "-l", "9000"]