db.createUser({
  user: "test_gen_user",
  pwd: process.env.MONGO_PASSWORD,
  roles: [
    {
      role: "readWrite",
      db: "test_gen_db",
    },
  ],
});

db.createCollection("test_patterns");
db.test_patterns.createIndex({ pattern_name: 1 }, { unique: true });
