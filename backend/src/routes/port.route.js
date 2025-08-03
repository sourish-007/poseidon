import { Router } from "express";
import { displayPorts } from "../controllers/port.controller.js";

const router = Router();

router.get("/display-ports", displayPorts);

export default router;