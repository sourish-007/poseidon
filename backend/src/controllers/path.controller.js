import { Port } from "../models/port.model.js";
import { axiosInstance } from "../lib/axios.js";

export const findPath = async (req, res) => {
  try {
    const { sourceid, destinationid } = req.params;

    if (!sourceid || !destinationid) {
      return res.status(400).json({ message: "Route parameters are missing." });
    }

    const sourcePort = await Port.findOne({ code: new RegExp(`^${sourceid}$`, 'i') });
    const destinationPort = await Port.findOne({ code: new RegExp(`^${destinationid}$`, 'i') });

    if (!sourcePort || !destinationPort) {
      return res.status(404).json({ message: "Source or destination port not found." });
    }

    const payload = {
      start: {
        lat: sourcePort.latitude,
        lng: sourcePort.longitude,
      },
      end: {
        lat: destinationPort.latitude,
        lng: destinationPort.longitude,
      },
    };

    const { data } = await axiosInstance.post('/path/find', payload);

    return res.status(200).json(data);

  } catch (error) {
    if (error.response) {
      return res.status(error.response.status).json(error.response.data);
    }
    return res.status(500).json({ message: "Internal Server Error" });
  }
};