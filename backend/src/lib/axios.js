import axios from "axios";

export const axiosInstance = axios.create({
    baseURL: "http://127.0.0.1:5001",
    withCredentials: true,
     headers: {
        'Content-Type': 'application/json'
    }
});