import * as React from "react"

import { apiConnector, echoConnector } from "./connectors"

export class Placeholder extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      message: "",
      things: [],
      error: ""
    }
  }
  componentDidMount() {
    apiConnector.listThings()
      .then((response) => {
        this.setState({ things: response.data.data });
      })
      .catch((error) => {
        this.setState({ error: error.toString() });
      })
    this.messageHandler = (message) => {
      this.setState((oldState) => ({ things: oldState.things.concat([{ text: message }]) }))
    }
    echoConnector.on("message", this.messageHandler)
  }
  componentWillUnmount() {
    echoConnector.off("message", this.messageHandler)
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ color: "red" }}>{this.state.error}</div>
      )
    }
    else {
      return (
        <div>
          <div>A few of my favorite things...</div>
          <div>
            {this.state.things.map((ele) => (<li key={ele.text}>{ele.text}</li>))}
          </div>
          <div>
            <form onSubmit={(event) => this.handleMessageSubmit(event)}>
              <input type="text" placeholder="Send a message"
                  value={this.state.message}
                  onChange={(event) => this.handleMessageChange(event)} />
            </form>
          </div>
        </div>
      )
    }
  }
  handleMessageChange(event) {
    this.setState({ message: event.target.value })
  }
  handleMessageSubmit(event) {
    event.preventDefault()
    echoConnector.send(this.state.message)
    this.setState({ message: "" })
  }
}
