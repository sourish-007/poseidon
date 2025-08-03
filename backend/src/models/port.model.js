import mongoose from "mongoose";

const portSchema = new mongoose.Schema({
  countryName: {
    type: String,
    required: true,
  },
  portName: {
    type: String,
    required: true,
  },
  code: {
    type: String,
    required: true,
    unique: true,
  },
  latitude: {
    type: Number,
    required: true,
  },
  longitude: {
    type: Number,
    required: true,
  },
});

export const Port = mongoose.model("Port", portSchema);