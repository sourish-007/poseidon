import { Port } from '../models/port.model.js';

export const displayPorts = async (req, res) => {
    try {
        const allPorts = await Port.find({});
        res.status(200).json(allPorts);
    } catch (error) {
        res.status(500).json({ message: "Error fetching port data" });
    }
};