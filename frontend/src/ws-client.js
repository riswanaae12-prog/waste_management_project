// install: npm install socket.io-client
import { io } from "socket.io-client";

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || "http://localhost:6000";
const socket = io(SOCKET_URL, { transports: ["websocket"] });

export function subscribeToTelemetry(onMessage) {
  socket.on("connect", () => console.log("ws connected"));
  socket.on("telemetry", (data) => {
    try { onMessage(data); } catch (e) { console.error(e); }
  });
  socket.on("disconnect", () => console.log("ws disconnected"));
  return () => {
    socket.off("telemetry");
    socket.disconnect();
  };
}