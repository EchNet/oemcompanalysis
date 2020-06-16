import axios from "axios";
import ImportedCookies from "cookies-js";


const FRESH_MILLIS = 5*60*1000;  // 5 minutes
const REFRESHABLE_MILLIS = 23*60*60*1000;  // 23 hours


class ApiConnector {
  constructor() {
    this.jwt = ImportedCookies.get("jwt")
    this.jwt_tob = Number(ImportedCookies.get("jwt_tob"))
  }
  getJwt() {
    let doRefresh = false;
    if (this.jwt && this.jwt_tob) {
      if (new Date().getTime() - this.jwt_tob < FRESH_MILLIS) {
        return Promise.resolve(this.jwt);
      }
      else if (new Date().getTime() - this.jwt_tob < REFRESHABLE_MILLIS) {
        doRefresh = true;
      }
    }
    const callForToken = doRefresh
      ? axios.post("/api/1.0/auth-jwt-refresh", { token: this.jwt }, {})
      : axios.post("/api/1.0/auth-jwt", {}, {
          withCredentials: true,
          headers: {
            "X-CSRFToken": ImportedCookies.get("csrftoken"),
          }
      })
    return callForToken.then((response) => {
      this.jwt = response.data.token;
      this.jwt_tob = new Date().getTime().toString();
      ImportedCookies.set("jwt", this.jwt)
      ImportedCookies.set("jwt_tob", this.jwt_tob)
      return this.jwt;
    })
  }
  _doGet(uri) {
    return this.getJwt().then((jwt) => axios.get("/api/1.0/thing", {
      headers: {
        Accept: "application/json",
        Authorization: `JWT ${jwt}`
      }
    }))
  }
  listThings() {
    return this._doGet("/api/1.0/thing")
  }
}

const formDataOptions = {
  withCredentials: true,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'multipart/form-data; boundary=--3xyNe89--',
    'X-CSRFToken': ImportedCookies.get('csrftoken'),
  },
};

export const apiConnector = new ApiConnector()
