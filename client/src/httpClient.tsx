import axios from "axios";

const authAxios = axios.create({
  withCredentials: true,
});

export default authAxios;
