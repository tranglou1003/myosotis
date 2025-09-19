# Chọn image Node.js 22
FROM node:22

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy package.json và package-lock.json
COPY package*.json ./

# Cài dependencies
RUN npm install --force

# Copy toàn bộ source code vào container
COPY . .

# Expose port ứng dụng chạy (mặc định Next.js hay Vite dùng 3000)
EXPOSE 5173

# Chạy ứng dụng ở chế độ phát triển
CMD ["npm", "run", "dev"]
