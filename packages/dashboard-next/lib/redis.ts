import Redis from "ioredis";

const getRedisClient = () => {
  if (process.env.REDIS_URL) {
    return new Redis(process.env.REDIS_URL);
  }
  return new Redis({
    host: "localhost",
    port: 6379,
  });
};

// Singleton pattern for Next.js (prevents multiple connections in dev)
declare global {
  var redis: Redis | undefined;
}

const redis = global.redis || getRedisClient();

if (process.env.NODE_ENV !== "production") {
  global.redis = redis;
}

export default redis;
