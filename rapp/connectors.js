import axios from "axios"
import ImportedCookies from "cookies-js"
import { w3cwebsocket as WebSocket } from "websocket"
import EventEmitter from "eventemitter3"


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


class EchoConnector extends EventEmitter {
  static getEndpoint() {
    const scheme = window.location.protocol == "https:" ? "wss" : "ws";
    return scheme + "://" + window.location.host + "/ws/echo/";
  }
  open() {
    if (this.client && this.client.readyState == WebSocket.OPEN) {
      return Promise.resolve(this.client)
    }
    if (!this.openPromise) {
      this.openPromise = new Promise((resolve, reject) => {
        const endpoint = EchoConnector.getEndpoint()
        this.client = new WebSocket(endpoint)
        this.client.onopen = () => {
          this.openPromise = null;
          this.emit("connect")
          resolve(this.client)
        }
        this.client.onclose = () => {
          this.emit("disconnect")
        }
        this.client.onmessage = (event) => {
          const data = JSON.parse(event.data)
          this.emit("message", data.message)
        }
      })
    }
    return this.openPromise;
  }
  send(message) {
    this.open().then((client) => {
      client.send(JSON.stringify({ type: "message", message }))
    })
  }
}


export const apiConnector = new ApiConnector()
export const echoConnector = new EchoConnector()
