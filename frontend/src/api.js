import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const runCode = async (code, stdin = "") => {
  const res = await API.post("/run", {
    code,
    stdin,
  });
  return res.data.output;
};
