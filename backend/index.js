import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import { ConnectDB } from "./src/lib/db.js";

import portRoutes from "./src/routes/port.route.js";
import pathRoutes from "./src/routes/path.route.js";

dotenv.config();

const app = express();

app.use(cors({
    origin: "http://localhost:5173", 
    credentials: true, 
}));

app.use(express.json());

app.use("/port", portRoutes);
app.use("/path", pathRoutes);

const PORT = process.env.PORT;

app.listen(PORT, () => {
    console.log(`Server running on port: ${PORT}`);
    ConnectDB();
});