import { Router } from "express";
import { findPath } from "../controllers/path.controller.js";

const router = Router();

router.post("/:sourceid/:destinationid/find-path", findPath);

export default router;