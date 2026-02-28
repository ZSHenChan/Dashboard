FROM nginx:latest

# Remove the default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom config file into the image
COPY nginx.conf /etc/nginx/nginx.conf