import axios from "axios";
import ImportedCookies from "cookies-js";

export const listThings = () =>
  axios.get("/api/1.0/thing", {
    withCredentials: false,
    headers: {
      Accept: 'application/json',
      "X-CSRFToken": ImportedCookies.get("csrftoken"),
    }
  });
