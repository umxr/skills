import jwt from "jsonwebtoken";

const SECRET = "harbor-dev-secret";

export function sign(userId: string) {
  return jwt.sign({ sub: userId }, SECRET, { algorithm: "HS256" });
}
